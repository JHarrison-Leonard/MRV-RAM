PRG                 = RAM-AVR
OBJ                 = main.o serialIO.o

MCU_TARGET          = atmega328p
OPTIMIZE            = -O2

DEFS                = -DF_CPU=16000000UL -DBAUD=19200
LIBS                =


CC                  = avr-gcc
override CFLAGS     = -g -Wall $(OPTIMIZE) -mmcu=$(MCU_TARGET) $(DEFS)
override LDFLAGS    = -Wl,-Map,$(PRG).map
OBJCOPY             = avr-objcopy


all: $(PRG).elf hex

$(PRG).elf: $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LIBS)


main.o: main.c main.h serialIO.h

serialIO.o: serialIO.c serialIO.h


clean:
	rm -rf *.o $(PRG).elf
	rm -rf *.hex *.map


hex:  $(PRG).hex

%.hex: %.elf
	$(OBJCOPY) -j .text -j .data -O ihex $< $@
