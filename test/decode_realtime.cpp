// test/decode_realtime.cpp
// qzssmsg.txtの実機データをデコードして結果を出力

#define ARDUINO 0
#include "../src/azaraC.h"
#include "../src/internal/Decoder.h"
#include "../src/internal/NmeaFramer.h"
#include "../src/internal/JsonSerializer.h"
#include "../src/internal/PrintShim.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>

using namespace azaraC;
using namespace azaraC::internal;

// ── Print → std::string アダプタ ────────────────────────────────────────────
struct StringPrint : public Print {
    std::string buf;
    size_t write(uint8_t c) override { buf += (char)c; return 1; }
    size_t write(const char* s, size_t size) override { if (s && size) buf.append(s, size); return size; }
    void print(char c)         override { write(c); }
    void print(const char* s)  override { if (s) buf += s; }
    void print(int v)          override { buf += std::to_string(v); }
    void print(unsigned int v) override { buf += std::to_string(v); }
    void println()             override { buf += '\n'; }
};

// ── NMEAデコードヘルパー ─────────────────────────────────────────────────────
struct DecodeResult {
    bool ok;
    bool valid;
    int msg_type;
    int svid;
    int disaster_category;  // MT=43用
    int service_kind;       // MT=44用
    std::string json;
    std::string error;
};

DecodeResult decodeNmea(const char* nmea_str, uint32_t now = 0) {
    DecodeResult result{};
    result.ok = false;
    result.valid = false;
    result.msg_type = 0;
    result.svid = 0;
    result.disaster_category = 0;
    result.service_kind = 0;
    
    NmeaFramer framer;
    Frame frame;
    
    for (int i = 0; nmea_str[i]; i++) {
        if (framer.feed((uint8_t)nmea_str[i], frame)) {
            Decoder dec;
            Message msg{};
            result.ok = dec.decode(frame, msg, now);
            result.valid = msg.valid;
            result.msg_type = msg.msg_type;
            result.svid = msg.svid;
            
            if (result.ok && result.valid) {
                if (msg.msg_type == 43) {
                    result.disaster_category = msg.mt43.disaster_category;
                } else if (msg.msg_type == 44) {
                    result.service_kind = (int)msg.mt44.service_kind;
                }
                
                StringPrint sp;
                JsonSerializer::serialize(msg, sp);
                result.json = sp.buf;
            }
            return result;
        }
    }
    
    result.error = "NMEA frame not found";
    return result;
}

// ログ行からNMEAデータを抽出
std::string extractNmea(const std::string& line) {
    // "$QZQSM," を探す
    size_t start = line.find("$QZQSM,");
    if (start == std::string::npos) return "";
    
    // 終わりまで抽出（*XXの後まで）
    size_t end = line.find('*', start);
    if (end == std::string::npos) return "";
    
    // *XX まで含める（2文字のチェックサム）
    end += 3;
    
    return line.substr(start, end - start);
}

int main() {
    printf("========================================\n");
    printf(" 実機データデコード結果\n");
    printf("========================================\n\n");
    
    // ファイルを開く（ワークスペースルートから）
    std::ifstream file("../qzssmsg.txt");
    if (!file.is_open()) {
        printf("エラー: qzssmsg.txtを開けません\n");
        return 1;
    }
    
    std::string line;
    int line_num = 0;
    int success_count = 0;
    int fail_count = 0;
    int skip_count = 0;
    
    // 重複排除用
    std::vector<std::string> processed_nmea;
    
    while (std::getline(file, line)) {
        line_num++;
        
        // NMEAデータを抽出
        std::string nmea = extractNmea(line);
        if (nmea.empty()) {
            skip_count++;
            continue;
        }
        
        // 重複チェック（同じNMEAデータはスキップ）
        bool duplicate = false;
        for (const auto& prev : processed_nmea) {
            if (prev == nmea) {
                duplicate = true;
                break;
            }
        }
        if (duplicate) continue;
        processed_nmea.push_back(nmea);
        
        // デコード
        DecodeResult result = decodeNmea(nmea.c_str());
        
        printf("----------------------------------------\n");
        printf("NMEA: %s\n", nmea.c_str());
        
        if (result.ok && result.valid) {
            printf("結果: 成功\n");
            printf("  msg_type: %d\n", result.msg_type);
            printf("  svid: %d\n", result.svid);
            
            if (result.msg_type == 43) {
                const char* dc_names[] = {
                    "不明", "EEW", "震源", "震度", "南海トラフ", "津波",
                    "北西太平洋津波", "長周期地震動", "火山", "降灰",
                    "気象", "洪水", "台風", "不明", "海上"
                };
                int dc = result.disaster_category;
                const char* dc_name = (dc >= 0 && dc <= 14) ? dc_names[dc] : "不明";
                printf("  disaster_category: %d (%s)\n", dc, dc_name);
            } else if (result.msg_type == 44) {
                const char* sk_names[] = {
                    "NULL", "L-Alert", "J-Alert", "LocalGov", "OutsideJapan", "Unknown"
                };
                int sk = result.service_kind;
                const char* sk_name = (sk >= 0 && sk <= 5) ? sk_names[sk] : "不明";
                printf("  service_kind: %d (%s)\n", sk, sk_name);
            }
            
            printf("  JSON: %s\n", result.json.c_str());
            success_count++;
        } else {
            printf("結果: 失敗 (%s)\n", result.error.empty() ? "デコードエラー" : result.error.c_str());
            fail_count++;
        }
    }
    
    file.close();
    
    printf("\n========================================\n");
    printf(" サマリー\n");
    printf("========================================\n");
    printf("総行数: %d\n", line_num);
    printf("スキップ: %d\n", skip_count);
    printf("重複除外後: %d\n", (int)processed_nmea.size());
    printf("デコード成功: %d\n", success_count);
    printf("デコード失敗: %d\n", fail_count);
    
    return 0;
}
