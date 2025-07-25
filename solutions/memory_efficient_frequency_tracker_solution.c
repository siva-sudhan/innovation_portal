#include <stdint.h>
#include <string.h>

/* Track frequencies of 8-bit sensor readings in a packed table.
 *
 * `freq_table` must point to at least 128 bytes of memory even though the
 * function signature shows 256. Each byte holds two 4-bit frequency counts:
 *   - lower nibble for even-indexed value
 *   - upper nibble for odd-indexed value
 */
void track_frequencies(uint8_t readings[], int size, uint8_t freq_table[256])
{
    /* zero the used portion (128 bytes) */
    memset(freq_table, 0, 128);

    for (int i = 0; i < size; ++i) {
        uint8_t val = readings[i];
        int byte_idx = val / 2;
        int upper = val % 2;

        uint8_t current = freq_table[byte_idx];
        uint8_t count = upper ? (current >> 4) & 0x0F : current & 0x0F;

        if (count < 15) {
            count++;
            if (upper)
                current = (current & 0x0F) | (count << 4);
            else
                current = (current & 0xF0) | count;
            freq_table[byte_idx] = current;
        }
    }
}

/* Helper to read back the packed 4-bit frequency for a given value. */
uint8_t get_frequency(uint8_t freq_table[], uint8_t value)
{
    int byte_idx = value / 2;
    int upper = value % 2;
    uint8_t current = freq_table[byte_idx];
    return upper ? (current >> 4) & 0x0F : current & 0x0F;
}
