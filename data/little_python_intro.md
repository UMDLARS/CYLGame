# LARS' Apple Hunt

## Introduction

Your brand new robot, a LARS (Laboratory for Advanced Systems Research) model JB334, (displayed with a `@`) is on the ground in an field full of apples (displayed with a `O`). The only problem is, your robot doesn't know where to go! Robot's current program drives around randomly, which isn't very good for finding apples, especially since your robot can only take **300** steps before its batteries go dead. 

**You are a programmer for LARS! Your job: write a program to help your robot finds the apples!**

## The Default Program

### Random and the Modulo (Remainder) Operator

Your robot is programmed in Little Python (LP), a variant of the Python programming language. 

The first thing your robot does is generates a random number between 0 and 3 (0, 1, 2 or 3). 

    a = rand % 4

The above code picks one of four numbers using two things -- `rand` and the *modulo* operator `%`. 

The special `rand` variable always returns a random number every time it is read. 

The *modulo* operator can be thought of as "division remainder". So, `4 % 3` is *1*, because `4 / 3` has a remainder of 1. 

If you take a random number from `rand` and apply `% 4` to it, you will end up with a random number between 0 and 3 (try it on a piece of paper to convince yourself!). That random number is saved into the variable `a` using the assignment operation `a = rand % 4`.

### Conditionals: The 'if' Statement

Once your robot has a random number between 0 and 3, it can test that value using the `if` statement and choose to go in one of four directions based on the random number selected.

In an `if` statement, a program asks a question. If the question is **true**, the program executes the code between the curly braces (`{` and `}`). If the question is **false**, nothing happens.

So, the code:

    if x is y {
      z = 3
    }

... will set `z` to 3 *if and only if* the value of `x` equals the value of `y`. **Please note**: the conditional and left bracket (`{`) must be on the first line, followed by the conditional code (here `z = 3`) and finally by the right bracket (`}`) on its own line. 

In addition to `is`, you can test whether something `is not` something else.

Here's the first conditional statement from the default program:


    if a is 0 {
      move = east
    }


This code says "if the variable `a` is equal to *0*, set the variable `move` to *east*." (Remember, `a` was set using `rand` and the modulo (`%`) operator.  

The remaining 3 `if` statements cover west, north and south.

    if a is 1 { 
      move = west 
    } 
    if a is 2 { 
      move = north 
    } 
    if a is 3 { 
      move = south 
    } 

As you may have already guessed, your robot will move in whatever direction the variable `move` is set at the end of your program. Your program will run **300** times, and your score is the number of apples your robot manages to find during that time.

Of course, your current program just walks around randomly. So it's not very good.


## Level 1: Helping Your Robot Find Apples

Your LARS-JB334 robot comes with two apple-detecting sensors. One sensor, `x_dir` tells you whether the closest apple is to the west (left) or the east (right). The other sensor, `y_dir` tells you if the closest apple is to the north (up) or south (down). `x_dir` and `y_dir` equal 0 if you are directly in line with an apple in the given direction.

You can test `x_dir` and `y_dir` using a conditional `if` statement! 

For example:

    if x_dir is east {
         move = east
    }

... checks to see if `x_dir` says that the closest apple is to the east, and if it it is, sets the move to be east.

By creating conditionals that test `x_dir` and `y_dir` for `west`, `north` and `south` (and set `move` accordingly) your robot will walk **directly** towards the closest apple! Try it out for yourself!

**NOTE:** After you change your program, press the `Submit` button.

## Level 2: Avoiding Pits!

Once you clear the first level of apples, things get a little more complicated: Level 2 and above have apples, but they also have **pit traps!** If your LARS-JB334 robot falls into a pit, it breaks and the game ends.

Fortunately, your robot also comes equipped with four pit detectors: `pit_to_north`, `pit_to_south`, `pit_to_east`, and `pit_to_west`. By adding some additional conditional `if` statements (and setting `move` to avoid them), you can make sure that your robot won't step into a pit!

# Little Python Reference

Little Python (LP) is a stripped down version of Python.

## Variables

Variables hold boolean (true/false) or integer (whole number) values and persist across invocations of your program (that is, `move` will start your program being set to whatever it was set on the previous turn).

Variable names can contain alphanumeric characters and underscore (so a-z, A-Z, 0-9 and \_) but must start with an underscore (_) or a letter.

## Operators
### Logical Operators

#### is
LP supports the logical tests `is` (instead of the more common ==) and `is not` (instead of !=). LP also supports logical `or` and logical `and`. Logical tests evaluate to **true** or **false**. So, the logical statement `1 is 1` is **true**, because 1 doesn't equal 2. 

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
