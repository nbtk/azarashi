#pragma once
// azaraC - src/internal/PrintShim.h
// Minimal Arduino Print shim for host-side unit tests.

#if !defined(ARDUINO) || ARDUINO < 1
#include <cstdio>
#include <cstdint>
#include <string_view>

class Print {
public:
    virtual ~Print() = default;
    virtual size_t write(uint8_t c) { putchar(c); return 1; }
    virtual size_t write(const char* s, size_t size) { if (s && size) return fwrite(s, 1, size, stdout); return 0; }
    virtual void print(char c)         { write(c); }
    virtual void print(const char* s)  { if (s) fputs(s, stdout); }
    virtual void print(std::string_view s) { if (!s.empty()) write(s.data(), s.size()); }
    virtual void print(int v)          { printf("%d", v); }
    virtual void print(unsigned int v) { printf("%u", v); }
    virtual void println()             { putchar('\n'); }
    virtual void println(const char* s){ if (s) fputs(s, stdout); putchar('\n'); }
    virtual void println(std::string_view s) { print(s); putchar('\n'); }
    virtual void print(const void* s)  { if (s) fputs(static_cast<const char*>(s), stdout); }
};

#define F(s) (s)
#endif
