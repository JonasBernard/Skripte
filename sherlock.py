quadratzahlen = []



def quadratzahlen_generieren(von, bis):
	for i in range(von, bis):
		quadratzahlen.append(i ** 2)


def sherlock(x):
	if x/2 + 1 in quadratzahlen and x + 1 in quadratzahlen:
		return True
	return False


quadratzahlen_generieren(25, 50)
for i in quadratzahlen:
	print("Überprüfe {0}".format(i - 1))
	if sherlock(i - 1):
		print("Bedingung erfüllt für " + str(i - 1))
	else:
		print("Bedingung nicht erfüllt für " + str(i - 1))
