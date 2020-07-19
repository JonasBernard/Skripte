def fizzbuzz(max: int):
    for i in range(1, max + 1):
        output = ""  # Create the word that may be output later
        if i % 3 == 0:  # Check for multiples of 3
            output += "Fizz"
        if i % 5 == 0:  # Check for multiples of 5
            output += "Buzz"
        if output == "":  # If none of the above is true, output just the digit
            print(i)
        else:
            print(output)


fizzbuzz(100)  # Run FIzzBuzz from 1 to 100
