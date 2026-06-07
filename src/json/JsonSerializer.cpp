// azaraC - src/internal/JsonSerializer.cpp
// Top-level JSON serializer entry point

#include "../include/internal/JsonSerializer.h"
#include "../include/internal/JsonWriter.h"
#include "../include/definition/_index.h"
#include <optional>
#include <string_view>

namespace azaraC {
namespace internal {

// Forward declarations (defined in separate files)
void serializeDcx(const Message& m, Print& out);
void serializeEEW(const Message& m, Print& out);
void serializeHypocenter(const Message& m, Print& out);
void serializeSeismic(const Message& m, Print& out);
void serializeNankai(const Message& m, Print& out);
void serializeTsunami(const Message& m, Print& out);
void serializeNwPacTsu(const Message& m, Print& out);
void serializeVolcano(const Message& m, Print& out);
void serializeAshFall(const Message& m, Print& out);
void serializeWeather(const Message& m, Print& out);
void serializeFlood(const Message& m, Print& out);
void serializeTyphoon(const Message& m, Print& out);
void serializeMarine(const Message& m, Print& out);

// ---------------------------------------------------------------------------
// Top-level serialize
// ---------------------------------------------------------------------------
void JsonSerializer::serialize(const Message& msg, Print& out) {
    using namespace azaraC::def;
    out.print('{');
    wf_u(out, "svid",     msg.svid);
    wf_u(out, "msg_type", msg.msg_type);
    wf_u(out, "crc24",    msg.crc24);

    if (msg.msg_type == 44) {
        serializeDcx(msg, out);

    } else if (msg.msg_type == 43) {
        const Mt43Data& d = msg.mt43;
        wf_u(out, "report_classification", d.report_classification);
        wf_s(out, "report_classification_label",
            qzss_dcr_jma_report_classification_lookup(d.report_classification));
        wf_u(out, "disaster_category", d.disaster_category);
        wf_s(out, "disaster_category_label",
            qzss_dcr_jma_disaster_category_lookup(d.disaster_category));
        wf_u(out, "information_type", d.information_type);
        wf_s(out, "information_type_label",
            qzss_dcr_jma_information_type_lookup(d.information_type));
        writeDHM(out, "report_time", d.event_time);
        wk(out, "detail"); out.print('{');
        switch (d.disaster_category) {
            case  1: serializeEEW       (msg, out); break;
            case  2: serializeHypocenter(msg, out); break;
            case  3: serializeSeismic   (msg, out); break;
            case  4: serializeNankai    (msg, out); break;
            case  5: serializeTsunami   (msg, out); break;
            case  6: serializeNwPacTsu  (msg, out); break;
            case  8: serializeVolcano   (msg, out); break;
            case  9: serializeAshFall   (msg, out); break;
            case 10: serializeWeather   (msg, out); break;
            case 11: serializeFlood     (msg, out); break;
            case 12: serializeTyphoon   (msg, out); break;
            case 14: serializeMarine    (msg, out); break;
            default: wf_s(out, "note", "unsupported_category", /*last=*/true); break;
        }
        out.print('}');  // detail

    } else {
        wf_s(out, "note", "unsupported_msg_type", /*last=*/true);
    }

    out.print('}');
}

} // namespace internal
} // namespace azaraC
