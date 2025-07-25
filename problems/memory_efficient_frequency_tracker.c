/*
 * Problem: Memory-Efficient Frequency Tracker for 8-bit Values
 *
 * You’re designing firmware for a device that processes 8-bit sensor readings
 * (values from 0 to 255). You are constrained to use only 1KB (1024 bytes)
 * of memory to track the frequency of each possible value.
 *
 * Implement the function:
 *
 *     void track_frequencies(uint8_t readings[], int size,
 *                            uint8_t freq_table[256]);
 *
 * The twist: Only 512 bytes are available for the frequency table. Each
 * frequency can be at most 15 (4 bits). Therefore each byte in the table stores
 * two frequency counts packed as two 4-bit values.
 *
 * Bonus: Provide a helper function
 *
 *     uint8_t get_frequency(uint8_t freq_table[], uint8_t value);
 *
 * that returns the frequency of a given sensor value from the packed table.
 */
