#pragma once
// azaraC - src/internal/PrintShim.h
// Minimal Arduino Print shim for host-side unit tests.

#if !defined(ARDUINO) || ARDUINO < 1
#include <cstdio>
#include <cstring>
#include <cstdint>

class Print {
public:
    virtual ~Print() = default;
    virtual void print(char c)         { putchar(c); }
    virtual void print(const char* s)  { if (s) fputs(s, stdout); }
    virtual void print(int v)          { printf("%d", v); }
    virtual void print(unsigned int v) { printf("%u", v); }
    virtual void println()             { putchar('\n'); }
    virtual void println(const char* s){ if (s) fputs(s, stdout); putchar('\n'); }
    virtual void print(const void* s)  { if (s) fputs(static_cast<const char*>(s), stdout); }
};

#define F(s) (s)
#endif
