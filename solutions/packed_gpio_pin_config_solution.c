#include <stdint.h>

/* Set the configuration bits for a given GPIO pin.
 * `reg`  : pointer to the 64-bit packed register
 * `pin`  : pin number (0-31)
 * `config`: 2-bit configuration value (0-3)
 */
void set_pin_config(uint64_t *reg, int pin, uint8_t config)
{
    uint64_t mask = 0x3ULL << (pin * 2);
    *reg = (*reg & ~mask) | (((uint64_t)(config & 0x3)) << (pin * 2));
}

/* Retrieve the configuration of a GPIO pin from the packed register. */
uint8_t get_pin_config(uint64_t reg, int pin)
{
    return (reg >> (pin * 2)) & 0x3;
}
