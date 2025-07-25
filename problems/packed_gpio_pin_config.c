/*
 * Problem: Packed GPIO Pin Configuration Table
 *
 * You’re building firmware for a 32-pin GPIO controller.
 * Each pin has a 2-bit configuration:
 *   00 = Input
 *   01 = Output
 *   10 = Alternate Function
 *   11 = Analog
 *
 * Objectives:
 *   1. Store the configuration of all 32 GPIOs in a single 64-bit register.
 *   2. Implement functions to set and get a pin’s configuration.
 *
 * Required Functions:
 *   void set_pin_config(uint64_t *reg, int pin, uint8_t config);
 *     - pin: 0 to 31
 *     - config: 0 to 3 representing one of the four modes above
 *
 *   uint8_t get_pin_config(uint64_t reg, int pin);
 *     - returns the 2-bit configuration value for the given pin.
 *
 * Each pin uses two bits within the 64-bit register:
 *   Pin 0 -> bits 1:0
 *   Pin 1 -> bits 3:2
 *   ...
 *   Pin n -> bits (2n+1):(2n)
 *
 * To set a pin configuration:
 *   1. Clear the relevant two bits using a mask.
 *   2. OR in the new configuration shifted into position.
 *
 * To get a pin configuration:
 *   1. Shift the register right by (2 * pin) bits.
 *   2. Mask the result with 0x3 to obtain the 2-bit value.
 */
