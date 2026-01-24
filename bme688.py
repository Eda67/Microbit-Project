from microbit import i2c, sleep
import struct
import math
write_buf = bytearray(2)
baseLinesSet, tempRaw, pressureRaw, humidityRaw, gasResRaw, gasRange = False, 0, 0, 0, 0, 0
def get_uint8(reg):
	i2c.write(0x77, bytearray([reg]))
	return i2c.read(0x77, 1)[0]
def get_int8(reg):
	i2c.write(0x77, bytearray([reg]))
	return struct.unpack('b', i2c.read(0x77, 1))[0]
def twos_comp(val, bits):
	return val - (1 << bits) if val & (1 << (bits - 1)) else val
def i2c_write(reg, data):
	i2c.write(0x77, bytearray([reg, data]))
PAR_T1, PAR_T2, PAR_T3 = twos_comp((get_uint8(0xEA) << 8) | get_uint8(0xE9), 16), twos_comp((get_uint8(0x8B) << 8) | get_uint8(0x8A), 16), get_int8(0x8C)
PAR_P1, PAR_P2, PAR_P3, PAR_P4, PAR_P5 = (get_uint8(0x8F) << 8) | get_uint8(0x8E), twos_comp((get_uint8(0x91) << 8) | get_uint8(0x90), 16), get_int8(0x92), twos_comp((get_uint8(0x95) << 8) | get_uint8(0x94), 16), twos_comp((get_uint8(0x97) << 8) | get_uint8(0x96), 16)
PAR_P6, PAR_P7, PAR_P8, PAR_P9, PAR_P10 = get_int8(0x99), get_int8(0x98), twos_comp((get_uint8(0x9D) << 8) | get_uint8(0x9C), 16), twos_comp((get_uint8(0x9F) << 8) | get_uint8(0x9E), 16), get_int8(0xA0)
parH1_LSB_parH2_LSB = get_uint8(0xE2)
PAR_H1, PAR_H2, PAR_H3, PAR_H4, PAR_H5, PAR_H6, PAR_H7 = (get_uint8(0xE3) << 4) | (parH1_LSB_parH2_LSB & 0x0F), (get_uint8(0xE1) << 4) | (parH1_LSB_parH2_LSB >> 4), get_int8(0xE4), get_int8(0xE5), get_int8(0xE6), get_int8(0xE7), get_int8(0xE8)
PAR_G1, PAR_G2, PAR_G3, RES_HEAT_RANGE, RES_HEAT_VAL = get_int8(0xED), twos_comp((get_uint8(0xEC) << 8) | get_uint8(0xEB), 16), get_uint8(0xEE), (get_uint8(0x02) >> 4) & 0x03, twos_comp(get_uint8(0x00), 8)
def calc_t_fine():
	var1 = (tempRaw >> 3) - (PAR_T1 << 1)
	return (((var1 * PAR_T2) >> 11) + ((((var1 >> 1) * (var1 >> 1)) >> 12) * (PAR_T3 << 4) >> 14))
def calc_temperature():
	return REG_Temp
def calc_pressure():
	var1 = (calc_t_fine() >> 1) - 64000
	var2 = ((((var1 >> 2) * (var1 >> 2)) >> 11) * PAR_P6) >> 2
	var2 += ((var1 * PAR_P5) << 1)
	var2 = (var2 >> 2) + (PAR_P4 << 16)
	var1 = (((((var1 >> 2) * (var1 >> 2)) >> 13) * (PAR_P3 << 5)) >> 3) + ((PAR_P2 * var1) >> 1)
	var1 = var1 >> 18
	var1 = ((32768 + var1) * PAR_P1) >> 15
	pRead = 1048576 - pressureRaw
	pRead = ((pRead - (var2 >> 12)) * 3125)
	pRead = math.floor(pRead / var1) << 1 if (pRead >= (1 << 30)) else math.floor((pRead << 1) / var1)
	pRead += ((((PAR_P9 * (((pRead >> 3) * (pRead >> 3)) >> 13)) >> 12) + (((pRead >> 2) * PAR_P8) >> 13) + (((pRead >> 8) * (pRead >> 8) * (pRead >> 8) * PAR_P10) >> 17) + (PAR_P7 << 7)) >> 4)
	return pRead
def calc_humidity():
	var3 = (humidityRaw - (PAR_H1 << 4) - (math.floor((REG_Temp * PAR_H3) / 100) >> 1)) * ((PAR_H2 * (math.floor((REG_Temp * PAR_H4) / 100) + math.floor((math.floor(REG_Temp * (math.floor((REG_Temp * PAR_H5) / 100))) >> 6) / 100) + ((1 << 14)))) >> 10)
	return (math.floor(((((var3 + (((((PAR_H6 << 7) + (math.floor((REG_Temp * PAR_H7) / 100))) >> 4) * (((var3 >> 14) * (var3 >> 14)) >> 10)) >> 1)) >> 10) * (1000)) >> 12) / 1000))
def convert_gas_target_temp(targetTemp):
	return (math.floor(((((math.floor((math.floor(((math.floor((REG_Temp * PAR_G3) / 10) << 8) + (((PAR_G1 + 784) * math.floor((math.floor(((PAR_G2 + 154009) * targetTemp * 5) / 100) + 3276800) / 10)) >> 1)) / (RES_HEAT_RANGE + 4))) / ((131 * RES_HEAT_VAL) + 65536)) - 250) * 34)) + 50) / 100))
def calc_gas_resistance():
	return ((math.floor((10000 * (262144 >> gasRange)) / (4096 + ((gasResRaw - 512) * 3)))) * 100)
def init_gas_sensor():
	i2c_write(0x5A, convert_gas_target_temp(300))
	i2c_write(0x64, 109)
	gasEnable = (get_uint8(write_buf[0]) & 0x20)
	i2c_write(0x71, (0x00 | gasEnable))
def calc_air_quality():
	currentTemp = REG_Temp
	ambTemp, gBase = (tempBase, gasBase) if baseLinesSet else (currentTemp, 0)
	gRes = calc_gas_resistance()
	hRead = calc_humidity()
	humidityOffset = hRead - 40
	temperatureOffset = currentTemp - ambTemp
	humidityRatio = (humidityOffset / 40) + 1
	temperatureRatio = temperatureOffset / ambTemp
	humidityScore = ((100 - hRead) / (100 - 40)) if humidityOffset > 0 else (hRead / 40)
	humidityScore *= 0.25 * 100
	gasRatio = 1e37 if gBase == 0 else (gRes / gBase)
	gasScore = gasRatio * (100 * (1 - 0.25)) if (gBase - gRes) > 0 else round(70 + (5 * (gasRatio - 1)))
	gasScore = min(gasScore, 75)
	iaqPercent = math.trunc(humidityScore + gasScore)
	iaqScore = (100 - iaqPercent) * 5
	eCO2Value = 250 * math.exp(0.012 * iaqScore)
	eCO2Value *= (humidityRatio + temperatureRatio) if humidityOffset > 0 and temperatureOffset > 0 else humidityRatio if humidityOffset > 0 else (temperatureRatio + 1)
	eCO2Value = math.trunc(eCO2Value)
	return iaqScore, iaqPercent, eCO2Value
def establish_baselines():
	global gasBase, tempBase, baseLinesSet
	gasResTotal, tempTotal = 0, 0
	for i in range(60):
		read_data_registers()
		tempTotal += REG_Temp
		gasResTotal += calc_gas_resistance()
		sleep(5000)
		print("Progress {}/60".format(i))
	gasBase, tempBase, baseLinesSet = math.trunc(gasResTotal / 60), math.trunc(tempTotal / 60), True
def read_data_registers():
	global tempRaw, pressureRaw, humidityRaw, gasResRaw, gasRange, REG_Temp
	o_sample_tp = get_uint8(write_buf[0])
	i2c_write(0x74, 0x01 | o_sample_tp)
	write_buf[0] = 0x1D
	while (get_uint8(write_buf[0]) & 0x80) >> 7 != 1:
		pass
	write_buf[0] = 0x2D
	tempRaw = (get_uint8(0x22) << 12) | (get_uint8(0x23) << 4) | (get_uint8(0x24) >> 4)
	pressureRaw = (get_uint8(0x1F) << 12) | (get_uint8(0x20) << 4) | (get_uint8(0x21) >> 4)
	humidityRaw = (get_uint8(0x25) << 8) | get_uint8(0x26)
	gasResRaw = (get_uint8(0x2C) << 2) | (get_uint8(0x2D) >> 6)
	gasRange = get_uint8(0x2D) & 0x0F
	REG_Temp = (((calc_t_fine() * 5) + 128) >> 8) / 100
def init_sensor():
	write_buf[0] = 0xD0
	while get_uint8(write_buf[0]) != 0x61:
		pass
	i2c_write(0xE0, 0xB6)
	sleep(1000)
	i2c_write(0x74, 0x00)
	i2c_write(0x72, 0x02)
	i2c_write(0x74, (0x02 << 5) | (0x05 << 2))
	i2c_write(0x75, 0x02 << 2)
	i2c_write(0x71, 0x20)
	read_data_registers()
