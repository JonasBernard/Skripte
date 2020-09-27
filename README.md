# Skripte

Dieses Repository enthält von mir (und Freunden) geschriebene kleine Skripte.

## Autobiographische Zahl

> [Eine autobiographische] Zahl ist [...] selbstbeschreibend, [da] sich die Zahl allein aus Kenntnis ihrer Ziffern rekonstruieren lässt.
[(Wikipedia)](https://de.wikipedia.org/wiki/Selbstbeschreibende_Zahl)

Wenn für jede Ziffer einer nartürlichen Zahl gilt, dass eine Ziffer an n-ter Stelle die Häufigkeit der Ziffer n-1 in dieser Zahl angibt, dann heißt
diese Zahl autobiographisch oder selbstbeschreibend.

### Einfach nachvollziehen lässt sich das an einem Beispiel:
2020 ist eine autobiographische Zahl, da sie 2 Zweien und 2 Nullen, aber keine Einsen und keine Dreien enthält.
Es gibt übrigens nur eine weitere vierstellige autobiographische Zahl, wie sich [diesem Wikipedia-Artikel](https://de.wikipedia.org/wiki/Selbstbeschreibende_Zahl)
entnehmen lässt.

Das Skript `autobiographische_zahl.py` bestimmt autobiographische Zahlen, indem es jede Zahl in einem angegebenen
Zahlenbereich auf die Bedingung für eine autobiographische Zahl hin überprüft.

`nils(zahl)` und `jonas(zahl)` sind Funktionen, die auf verschiedene Weise aus einer Zahl eine Liste ihrer Stellen erzeugen. Um die Laufzeit der beiden
Ansätze zu überprüfen, lässt die Funktion `speed_test()` 1.000.000 zufällig generierte Zahlen auf beide Algorithmen los, und vergleicht die Laufzeiten.

> Inspiriert durch [DorFusch](https://youtu.be/fKRqyh4Hh4U).

## FizzBuzz

Bei FizzBuzz wird von 1 an hoch gezählt, mit der Besonderheit, dass jede Zahl, die durch 3 teilbar ist durch "Fizz" und jede Zahl, die durch 5 teilbar ist
durch "Buzz" ersetzt wird. Sobald eine Zahl durch sowohl 3 als auch 5 teilbar ist, sagt man FizzBuzz.

`fizzbuzz.py` gibt die gesagten Zahlen bzw. Wörter nach diesen Reglen aus.

> Inspiriert durch [Tom Scott](https://youtu.be/QPZ0pIK_wsc).

## Sherlock

48 ist eine besondere Zahl. Man kann zu ihr 1 addieren, und erhält eine Quadratzahl. Nun macht diese Eigenschaft sie noch nicht besonders. Wenn man
die Zahl jedoch halbiert, erhält man erneut eine Zahl, auf die diese Eigenschaft zutrifft.

Welche ist nun nach 48 die nächstgrößere Zahl, die auf diese Weise besonders ist?

Das Skript `sherlock.py` berechnet die Antwort auf diese Frage.

> Inspiriert durch [Tim Dedopulos' "Sherlock Holmes' Rätseluniversum"](https://www.thalia.de/shop/home/artikeldetails/ID64483778.html).

## Sudoku

Sudokus machen vielen Manschen Spaß, aber auch Computern. In `sudoku.py` findet sich ein rekursives Skript, welches die Lösungen von Sudokus ermittelt.

> Inspiriert durch [Computerphile](https://www.youtube.com/user/Computerphile/).

## Zahlen quadrieren

Anstatt eine Zahl n mit sich selbst zu multiplizieren, um sie zu quadrieren, kann man sie auch zur Basis b
mit b = n schreiben und die Anzahl der Nullen verdoppeln. Das diese Methode jedoch höchst ineffizient ist, zeigt
das Sktipt `zahlen_quadrieren.py`.