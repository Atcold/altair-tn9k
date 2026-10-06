# Parts

Quantities cover the breadboard stages and the final panel for both backends, plus spares.

## Shift-register backend (sr)

| Part | Needed | Order | Notes |
|---|---|---|---|
| SN74HC595N (DIP-16) | 5 | 7 | LED shift registers |
| SN74HC165N (DIP-16) | 4 | 6 | Switch shift registers |
| Bourns 4609X-101-103LF | 4 | 6 | 8 × 10 kΩ bussed pull-ups, 9-pin SIP, one per 74HC165 |
| DIP-16 sockets | 9 | 12 | Swap dead chips without desoldering |
| 33 Ω resistors | 5 | 10 | Series resistors on the carrier, one per FPGA output |

## SPI-expander backend (mcp)

| Part | Needed | Order | Notes |
|---|---|---|---|
| MCP23S17-E/SP (DIP-28) | 5 | 7 | 16-bit SPI I/O expanders |
| DIP-28 sockets (0.3″) | 5 | 7 | |
| 10 kΩ resistors | 1 | 10 | Shared RESET pull-up |
| 33 Ω resistors | 3 | (above) | Series resistors on SCK, MOSI, CS_n |

## Common

| Part | Needed | Order | Notes |
|---|---|---|---|
| 5 mm red LEDs | 36 | 50 | |
| 1 kΩ resistors | 36 | 100 | Default LED current, ≈ 1.3 mA |
| 470 Ω resistors | 36 | 100 | Brighter option, ≈ 3 mA |
| 100 nF ceramic capacitors | 16 | 25 | One per chip (9 sr + 5 mcp) and one per connector |
| 10 µF capacitors | 2 | 5 | Bulk decoupling, one per connector |
| 2×7 IDC box headers, 2.54 mm | 2 | 4 | J1 on the carrier, J2 on the panel |
| 14-way IDC sockets | 2 | 4 | Crimped onto the ribbon |
| 14-way ribbon cable | 15 cm | 1 m | |
| Mini toggle, ON-OFF (SPST) or ON-ON (SPDT) | 16 | 18 | Address/data switches |
| Mini toggle, momentary (ON)-OFF-(ON) | 8 | 11 | Control switches; the most abused, so 3 spares |
| 8-way DIP switches | 2 | 2 | Breadboard stages only |
| 2.54 mm female headers | 2 | 4 | Socket the Tang Nano; check the length against the board |
| Tang Nano 9K | 1 | 1 extra | Spare, about $20 |

## Tools and consumables

- Breadboard and jumper wires
- Perfboard (later a PCB) for the carrier
- Solid hook-up wire, 0.5–0.65 mm diameter
- 8-channel USB logic analyser (about $10), used with PulseView

## Where to buy

- **DigiKey or Mouser:** ICs, resistor networks, sockets, capacitors, connectors, DIP switches, toggles. Exact parts, fast US shipping, no minimum.
- **Micro Center (Brooklyn, Queens):** breadboards, jumpers, LEDs, resistor kits, same day. Check IC stock online first.
- **Amazon:** breadboard kits, jumpers, logic analyser. Avoid for ICs.
- **AliExpress:** cheapest, weeks of shipping.

## Cost estimate

| Group | Approx. cost |
|---|---|
| Everything except toggles, both backends | $50–75 |
| Toggles, cheap (~$1 each) | ~$30 |
| Toggles, decent, e.g. C&K 7000 series ($5–10 each) | $150–280 |
| Spare Tang Nano 9K | ~$20 |

Buy one of each toggle type first to judge the feel before ordering all 29.
