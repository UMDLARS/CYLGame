
# Little Python Reference

Little Python (LP) is a stripped down version of Python.

## Variables

Variables hold boolean (true/false) or integer (whole number) values and persist across invocations of your program (that is, `move` will start your program being set to whatever it was set on the previous turn).

Variable names can contain alphanumeric characters and underscore (so a-z, A-Z, 0-9 and \_) but must start with an underscore (_) or a letter.

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
