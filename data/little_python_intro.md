
# Little Python Reference

Little Python (LP) is a stripped down version of Python.

## Variables

### Scalar Variables

A scalar variable is a name that holds a single boolean (true/false) or integer (whole number) value. A scalar variable persists across invocations of your program (that is, `move` will start your program being set to whatever it was set on the previous turn).

Variable names can contain alphanumeric characters and underscore (so a-z, A-Z, 0-9 and \_) but must start with an underscore (_) or a letter.

You can assign values to variables using the `=` or "assignment" operator. For example, to set the variable `x` to `1` and `y` to `true`:

     x = 1
     y = true
     
Assigning to a variable that exists *changes its value*. Assigning to a variable that does not exist *creates and assigns a value* to that variable.

### Array Variables
### One-Dimensional Arrays

LP supports arrays -- a list of scalar variables stored under one name that are accessed by specifying the element of the list you want. Arrays are accessed using the notation `a[n]` where `a` is the "name" of the array variable, the brackets (`[]`) indicate that you are accesssing a specific element of the array, and the number `n` specifies which element you want. Arrays are *0-indexed* -- meaning that the first element of an array is the *0th* element. So, if an array `a` contained the scalar values *1, 2* and *3* (in that order), then `a[0]` would be `1`, `a[1]` would be `2` and `a[2]` would be `3`. 

**Note:** You cannot create arrays yourself; you can only use an array if one is provided to you by the game. 

### Two-Dimensional Arrays

A two-dimensional (or 2D) array is an *array of arrays*. 2D arrays are commonly used to represent a grid (e.g., a game map) where each array represents a row and each element in the array represents the column of a grid. 

For example, imagine a 2D array named `grid` containing the numbers 1-9 with three numbers in each row. You can conceptualize the 2D array as looking like:

     [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]
     ]
     
Here's how you would access various cells in that 2D array:
 * top left: `grid[0][0]`
 * top right: `grid[0][2]`
 * center: `grid[1][1]`
 * bottom left: `grid[2][0]`
 * bottom right: `grid[2][2]`

Again, 2D arrays are commonly used in these programs to represent the game field, where the value stored in a cell represents the thing at that location in a map. While game-specific sensors can provide easy access to specific pieces of information, more advanced techniques use loops and functions (described elsewhere in this document) to search the game field 2D array (you might even call it a "game grid") to learn things about the game state, distance between two points, closest item of a particular type, and so on.

Finally, remember that you cannot create an array -- only use an array that is provided to you by the game.
     
## Operators
### Logical Operators

#### is
LP supports the logical tests `is` (instead of the more common ==) and `is not` (instead of !=). LP also supports logical `or` and logical `and`. Logical tests evaluate to **true** or **false**. So, the logical statement `1 is 1` is **true**, because 1 equals 1. 

#### is not

You can also use the `is not` operator. For example, `1 is not 2` is **true**, because 1 isn't 2.

#### not

Finally, you can use the `not` operator, which makes the logical value opposite to what it originally was. So, `not 1 is 2` is **true**, because `1 is 2` is false, and `not` inverts its value to **true*.

#### Logical statements with variables

Importantly, you can compare the content of variables. Suppose `x = 1` and `y = 2`. Then, `x is y` would be **false**, because `x is y` is equivalent to `1 is 2` (which is false). This allows us to store information in variables and then make decisions based on their values. (More on this in a second.)

#### Combining arithmetic and logic

You can combine arithmetic and logic. For example, `1 + 1 is 3` is **false**, because 1 + 1 doesn't equal 3. (I think it's 2.)


### Conditional Statements

The power of logical operators is that we can use them with the `if` statement to decide what code to execute. It's how programs "make decisions" or "choose" between two options.

This allows you to test multiple conditions, for example:

    if x is y and a is b {
      z = c
    }

... will set `z` to the value of `c` if and only if `x is y` **AND** `a is b`. Similarly:

    if x is y or a is b {
      z = c
    }

... will set `z` to the value of `c` if `x is y` **OR** if `a is b`. (In other words, it will set `z` to `c` if either condition is true.)

LP also supports the `else` condition. This allows you to execute some code if your conditional statement is false.

For example:

    if x is y {
      z = 3
    } else {
      z = 5
    }

... will set `z` to 3 if `x is y` -- otherwise it will set `z` to 5.

### Loops

Loops in a programming language allow a program to run a particular section of code a specified number of times. 

FIXME

### Functions

Functions allow programmers to create a piece of code -- a method for doing something (also called an algorithm) -- and give it a name that can be referenced later for easy reuse. Functions can take arguments that customize it's behavior in some way -- that tell the function how to behave within the constraints of the algorithm. In other words, functions are basically named programs *inside* of programs.

As an analogy, suppose you make omelets so frequently that you have it down to "a process" that you repeat every time you do it. That's sort of like a function in a program. Let's call your function `make_omelet`. But of course, you can make many different types of omelet, so `make_omelet` takes "arguments" (sometimes called "parameters") that change how the function operates. For example, you might be able call `make_omelet` in several ways, e.g., `make_omelet(veggie)`, `make_omelet(denver)` or `make_omelet(cheese)`. Inside your `make_omelet` "code" are rules for how to make each type of omelet. This is efficient, since most of the steps for making an omelet are the same, regardless of the type of omelet you're making.

FIXME

### Arithmetic

LP supports the standard arithmetic operations

  * addition -- `+`
  * subtraction -- `-`
  * division -- `/`
  * multiplication -- `*`
  * modulo -- `%`

### Order of Operation (Precedence)

Remember from math class how multiplication and division happen before addition and subtraction? Well, the same is true for programming languages. Thus,

    3 * 2 + 3

... equals **9** -- not **15**.

In LP, you can use parenthesis just like you can in algebraic arithmetic. Thus,

    3 * (2 + 3)

... actually **does** equal **15**.

You can also use parentheses to group logical statements.

As you write more programs in LP, you might wonder questions like "what happens first, assignment (`=`) or addition? Here is the list of operator precedence:

  1. =
  1. ()
  1. *,/,%
  1. +,-
  1. is, is not
  1. not
  1. and, or

## Troubleshooting
### Help! My robot doesn't do anything or does the wrong thing!

If your robot doesn't do anything or does the wrong thing, then your program is valid, but there's something wrong with the logic of your program. Look at your program to see if you can find a problem. 

### I got the message "Your bot ran into an error at runtime"

If you get this message, it means that something about your program is not allowed -- maybe you have a typo or you asked Little Python to do something it can't.
