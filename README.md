# Cybergames Youth League Game Framework (CYLGame)

# Introduction

The University of Minnesota Duluth Cybergames Youth League (UMDCYL) is an annual online competition for high-school and middle-school students where students compete against each other by writing programs to control agents inside various video games. The first year, UMDCYL used [Dirtbags Tanks](https://github.com/dirtbags/tanks) as our game. "Tanks" is a fun and dynamic game where students use a variant of [FORTH](https://en.wikipedia.org/wiki/Forth_(programming_language)), called FORF, to program tanks to do battle in an arena. Scores are kept for individual tanks over time, so as tank programs improve, player rank changes. 

We modified Tanks to provide a few game variants [to support multiple league matches](https://www.youtube.com/watch?v=9ckBQ3OMOS4&list=PLHnc49MScQBCHIYRS4O4oAll4wTTjVatL&index=2). The league was successful, however, we felt that mere variants of one game were not as interesting as distinctly different challenges, and the Tanks game did not lend itself to radically different games. One thing we really liked about Tanks is its use of FORF, because it was a "levelling agent" -- students who had programming experience had never worked with FORF (or probably any FORTH variant), which put all students on a more even playing field.

We decided to create our own framework based on [the libtcod Roguelike library](https://bitbucket.org/libtcod/libtcod) and Jon Beaulieu's [Little Python](https://github.com/derpferd/little-python) (LP) project. Libtcod provided a tile-based interface with a variety of helper functions, while LP provided us with a custom programming language. While FORF provided a challenge to programmers (thinking in stacks and using reverse notation is a unique experience for most programmers), we also appreciated that LP was more like traditional languages, perhaps lowering entry barriers for students and making their experience more directly transferrable to other languages. In the end, libtcod was removed, but its behavior and lo-fi aesthetic is still apparent in CYLGames.

We maintain a server running UMDCYL games, and are happy to allow others to use the machine. Just contact <pahp@d.umn.edu>.

# Games

We have created a number of games for the CYLGame framework, including:

* [Applehunt](https://github.com/UMDLARS/applehunt) -- a simple demo program (seek and navigate towards apples, avoiding traps)
* [Robots](https://github.com/UMDLARS/robots) -- a clone of the classic 80s videogame "[ROBOTS](https://en.wikipedia.org/wiki/Robots_(computer_game))"
* [Ski](https://github.com/UMDLARS/ski) -- a riff on [classic 2D skiing games](https://en.wikipedia.org/wiki/SkiFree)
* [Pac-Bot](https://github.com/UMDLARS/pac-bot) -- an implementation of [Pac-Man](https://en.wikipedia.org/wiki/Pac-Man)
* [Space Invaders](https://github.com/UMDLARS/space_invaders) -- an implementation of [the legendary game](https://en.wikipedia.org/wiki/Space_Invaders)
* [TRON](https://github.com/UMDLARS/tron) -- an implementation of the popular ["light cycle" / Snake game](https://en.wikipedia.org/wiki/Snake_(video_game_genre))

Creating your own games for the CYLGame framework is relatively easy; the best way to do it is to look at existing source code.

# Installing CYLGame and Playing a Game

See the [generic instructions for installing CYLGame and playing a game](https://github.com/UMDLARS/CYLGame/blob/master/INSTALL_GAME.md).
