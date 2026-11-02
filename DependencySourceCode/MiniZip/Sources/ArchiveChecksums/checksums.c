#include "include/checksums.h"

uint32_t minizip_crc32(const unsigned char *bytes, size_t count) {
    uint32_t checksum = UINT32_MAX;
    for (size_t i = 0; i < count; i++) {
        checksum ^= bytes[i];
        for (unsigned bit = 0; bit < 8; bit++) {
            checksum = (checksum >> 1) ^ ((checksum & 1) ? 0xedb88320 : 0);
        }
    }
    return checksum ^ UINT32_MAX;
}
