# PyRA

This library implements [**R**elational **A**lgebra](https://en.wikipedia.org/wiki/Relational_algebra) syntax in **Py**thon.

- expression tree visualization
- type validation
- query execution

## Introduction

Consider the simple database signature

```
 PERSON / (person_id, name, age)
STUDENT / (person_id, guardian_id)
```

where each student has at least one guardian.

Suppose we wanted a query to find the IDs of all students who have one or more guardians not yet 18 years old.
We could express this in relational algebra as

$$
\mathrm{elim}\!\left(
    \pi_{\\#1}\!\left(
        \texttt{STUDENT}
        \bowtie_{\\#1 = \\#2\ell}
        \sigma_{\\#3 < 18}\!\left(\texttt{PERSON}\right)
    \right)
\right)
\tag{1}
$$

or

$$
\mathrm{elim}\!\left(
    \pi_{\\#5}\!\left(
        \sigma_{\\#1 > \\#4, \\#2 = \\#6}\!\left(
            18 \times \texttt{PERSON} \times \texttt{STUDENT}
        \right)
    \right)
\right)
\tag{2}
$$

and so on.

On the other hand, expression $(3)$ below differs from $(1)$ by a single character, but it is invalid because it joins the wrong attributes.

$$
\mathrm{elim}\!\left(
    \pi_{\\#1}\!\left(
        \texttt{STUDENT}
        \bowtie_{\textcolor{red}{\\#1 = \\#1\ell}}
        \sigma_{\\#3 < 18}\!\left(\texttt{PERSON}\right)
    \right)
\right)
\tag{3}
$$

Meanwhile, expression $(4)$ below is perfectly legal, but still produces an incorrect result:

$$
\begin{aligned}
    &\mathrm{elim}\!\left(
        \pi_{\\#1}\!\left(
            \texttt{STUDENT}
        \right)
    \right) \\
    &- \mathrm{elim}\!\left(
        \pi_{\\#1}\!\left(
            \texttt{STUDENT}
            \bowtie_{\\#1 = \\#2\ell}
            \sigma_{\\#3 \geq 18}\!\left(\texttt{PERSON}\right)
        \right)
    \right)
\end{aligned}
\tag{4}
$$

Even though this example is meant to be *simple*, it is already difficult to tell the difference between a correct and incorrect relational algebra expression!

This library is born out of a desire to automatically verify arbitrary relational algebra queries.

## Setup

First, we convert the above schema into Python code.

### Attributes

Each attribute is represented by a list of string type names.
Type names are *semantic*.
For example, even though student IDs and guardian IDs are just person IDs, we specifically name those as types.

```py
student_id = Attribute("sid")
guardian_id = Attribute("gid")
person_id = Attribute("pid") | student_id | guardian_id
name = Attribute("name")
age = Attribute("age")
```

### Relations

A relation combines a sequence of attributes with some example elements of that relation.
We specifically set up the elements to test our query:

```py
PERSON = Relation(
    attributes=(person_id, name, age),
    elements=[
        (1, "S_1", 11), # has G<18
        (2, "S_2", 12), # has both guardians
        (3, "S_3", 13), # has G=18
        (4, "G<18", 17),
        (5, "G=18", 18),
    ],
)
# ( pid|sid|gid , name , age )
#   1           , S_1  , 11
#   2           , S_2  , 12
#   3           , S_3  , 13
#   4           , G<18 , 17
#   5           , G=18 , 18

STUDENT = Relation(
    attributes=(student_id, guardian_id),
    elements=[
        (1, 4),
        (2, 4),
        (2, 5),
        (3, 5),
    ],
)
# ( sid , gid )
#   1   , 4
#   2   , 4
#   2   , 5
#   3   , 5
```

### Query

In our query, we deal with the age constant `18`.
To prevent this constant from being compared with non-age numbers, we build a single-attribute (age) relation with `18` as the only value.

```py
AGE_OF_MAJORITY = ConstantRelation(age, 18)
```

We can also define the expected result of our query:

```py
expected = Relation(
    attributes=(student_id,),
    elements=[
        (1,),
        (2,),
    ],
)
# ( sid )
#   1
#   2
```

## Relational Algebra in Python

The following code demonstrates various relational algebra operations using examples.

### Selection ($\sigma$)

All people under the age of majority:

$$
    \sigma_{\\#3 \leq 18}\!\left(\texttt{PERSON}\right)
$$

where $\\#3$ refers to the third attribute of `PERSON`.

> Attributes are one-indexed.
> This allows us to do something nifty later on...

```py
select[3 |lt| AGE_OF_MAJORITY](PERSON)
# ( pid|sid|gid , name , age )
#   1           , S_1  , 11
#   2           , S_2  , 12
#   3           , S_3  , 13
#   4           , G<18 , 17
```

> `3 |lt| AGE_OF_MAJORITY` is an example of using the bitwise OR operation in Python to simulate custom infix operators such as `lt` here.
> For more details on this method, see [Tomer Filiba's blog](https://tomerfiliba.com/blog/Infix-Operators).

### Projection ($\pi$)

All names:

$$
    \pi_{\\#2}\!\left(\texttt{PERSON}\right)
$$

```py
project[2](PERSON)
# ( name )
#   S_1
#   S_2
#   S_3
#   G<18
#   G=18
```

### Elimination ($\mathrm{elim}$)

All *distinct* student IDs:

$$
    \mathrm{elim}\!\left(\pi_{\\#1}\!\left(\texttt{STUDENT}\right)\right)
$$

```py
eliminate(project[1](STUDENT))
# ( sid )
#   1
#   2
#   3
```

### Product ($\times$)

All possible pairs of elements from the relations `STUDENT` and `PERSON`:

$$
    \texttt{STUDENT} \times \texttt{PERSON}
$$

```py
STUDENT |product| PERSON
# ( sid , gid , pid|sid|gid , name , age )
#   1   , 4   , 1           , S_1  , 11
#   1   , 4   , 2           , S_2  , 12
#   1   , 4   , 3           , S_3  , 13
#   1   , 4   , 4           , G<18 , 17
#   1   , 4   , 5           , G=18 , 18
#   2   , 4   , 1           , S_1  , 11
#   2   , 4   , 2           , S_2  , 12
#   2   , 4   , 3           , S_3  , 13
#   2   , 4   , 4           , G<18 , 17
#   2   , 4   , 5           , G=18 , 18
#   2   , 5   , 1           , S_1  , 11
#   2   , 5   , 2           , S_2  , 12
#   2   , 5   , 3           , S_3  , 13
#   2   , 5   , 4           , G<18 , 17
#   2   , 5   , 5           , G=18 , 18
#   3   , 5   , 1           , S_1  , 11
#   3   , 5   , 2           , S_2  , 12
#   3   , 5   , 3           , S_3  , 13
#   3   , 5   , 4           , G<18 , 17
#   3   , 5   , 5           , G=18 , 18
```

### Join ($\bowtie$)

A join is equivalent to a product ($\times$) followed by a selection ($\sigma$).
For example, we could filter the product between `STUDENT` and `PERSON` on matching guardian ID:

$$
    \sigma_{\\#2 = \\#3}\!\left(\texttt{STUDENT} \times \texttt{PERSON}\right)
$$

or we could implement this as a join:

$$
    \texttt{STUDENT} \bowtie_{\\#1 = \\#2\ell} \texttt{PERSON}
$$

Where $\ell$ indicates an attribute index belonging to the relation on the left, while the absence of $\ell$ indicates an attribute index belonging to the relation on the right.
In this case, the index $\\#1 = \\#2\ell$ refers to
- $\\#1$: the first attribute of `PERSON`
- $\\#2\ell$: the second attribute of `STUDENT`

To express this in code, we use negative indices (e.g., $\\#2\ell \to \texttt{-2}$) to indicate the left argument.

```py
STUDENT |join[1 |eq| -2]| PERSON
# ( sid , gid , gid , name , age )
#   1   , 4   , 4   , G<18 , 17
#   2   , 4   , 4   , G<18 , 17
#   2   , 5   , 5   , G=18 , 18
#   3   , 5   , 5   , G=18 , 18
```

> Notice that the type of the first column of `PERSON` changed following the join.
> This library is smart enough to figure out that an equality-based selection condition (like $\\#1 = \\#2\ell$) will result in a type intersection between the participating columns.

### Difference ($-$)

All ages other than 18:

$$
    \pi_{\\#3}\!\left(\texttt{PERSON}\right)
    - 18
$$

```py
project[3](PERSON) |difference| AGE_OF_MAJORITY
# ( age )
#   11
#   12
#   13
#   17
```

### Union ($\cup$)

All students or guardians:

$$
    \pi_{\\#1}\!\left(\texttt{STUDENT}\right)
    \cup
    \pi_{\\#2}\!\left(\texttt{STUDENT}\right)
$$

```py
project[1](STUDENT) |union| project[2](STUDENT)
# ( sid|gid )
#   1
#   2
#   2
#   3
#   4
#   4
#   5
#   5
```

### Note on Order of Operations

The custom infix operators used in this library are implemented by overloading the bitwise OR operation `|`, which is evaluated left to right.

Because of this, we have limited control over the order of operations.
For example, there is no way to give higher precedence to product ($\times$) than difference ($-$).
When in doubt, use parentheses to enforce evaluation order.

## Query Verification

To come full circle, we now implement all 4 example RA expressions.

The `resolve` function lets us trace the evaluation tree of the expression on our sample database instance.

### Expression $(1)$: Correct

$$
\mathrm{elim}\!\left(
    \pi_{\\#1}\!\left(
        \texttt{STUDENT}
        \bowtie_{\\#1 = \\#2\ell}
        \sigma_{\\#3 < 18}\!\left(\texttt{PERSON}\right)
    \right)
\right)
$$

```py
eliminate(project[1](STUDENT |join[1 |eq| -2]| select[3 |lt| AGE_OF_MAJORITY](PERSON)))
# ┌─
# │ ┌─
# │ │ ┌─
# │ │ ┤ ( sid , gid )                   = ( sid , gid )
# │ │ ┤                                     1   , 4
# │ │ ┤                                     2   , 4
# │ │ ┤                                     2   , 5
# │ │ ┤                                     3   , 5
# │ │ ╞═
# │ │ ├ ┌─
# │ │ ├ │ ( pid|sid|gid , name , age )  = ( pid|sid|gid , name , age )
# │ │ ├ │                                   1           , S_1  , 11
# │ │ ├ │                                   2           , S_2  , 12
# │ │ ├ │                                   3           , S_3  , 13
# │ │ ├ │                                   4           , G<18 , 17
# │ │ ├ │                                   5           , G=18 , 18
# │ │ ├ ├─
# │ │ ├ σ[#3<18]                        = ( pid|sid|gid , name , age )
# │ │ ├                                     1           , S_1  , 11
# │ │ ├                                     2           , S_2  , 12
# │ │ ├                                     3           , S_3  , 13
# │ │ ├                                     4           , G<18 , 17
# │ │ ├─
# │ │ × σ[#1=#2l]                       = ( sid , gid , gid , name , age )
# │ │                                       1   , 4   , 4   , G<18 , 17
# │ │                                       2   , 4   , 4   , G<18 , 17
# │ ├─
# │ π[#1]                               = ( sid )
# │                                         1
# │                                         2
# ├─
# elim                                  = ( sid )
#                                           1
#                                           2
```

### Expression $(2)$: Correct

$$
\mathrm{elim}\!\left(
    \pi_{\\#5}\!\left(
        \sigma_{\\#1 > \\#4, \\#2 = \\#6}\!\left(
            18 \times \texttt{PERSON} \times \texttt{STUDENT}
        \right)
    \right)
\right)
$$

```py
eliminate(project[5](select[1 |gt| 4, 2 |eq| 6](AGE_OF_MAJORITY |product| PERSON |product| STUDENT)))
# ┌─
# │ ┌─
# │ │ ┌─
# │ │ │ ┌─
# │ │ │ ┤ ┌─
# │ │ │ ┤ ┤ 18                            = 18
# │ │ │ ┤ ╞═
# │ │ │ ┤ ├ ( sid|pid|gid , name , age )  = ( sid|pid|gid , name , age )
# │ │ │ ┤ ├                                   1           , S_1  , 11
# │ │ │ ┤ ├                                   2           , S_2  , 12
# │ │ │ ┤ ├                                   3           , S_3  , 13
# │ │ │ ┤ ├                                   4           , G<18 , 17
# │ │ │ ┤ ├                                   5           , G=18 , 18
# │ │ │ ┤ ├─
# │ │ │ ┤ ×                               = ( age , sid|pid|gid , name , age )
# │ │ │ ┤                                     18  , 1           , S_1  , 11
# │ │ │ ┤                                     18  , 2           , S_2  , 12
# │ │ │ ┤                                     18  , 3           , S_3  , 13
# │ │ │ ┤                                     18  , 4           , G<18 , 17
# │ │ │ ┤                                     18  , 5           , G=18 , 18
# │ │ │ ╞═
# │ │ │ ├ ( sid , gid )                   = ( sid , gid )
# │ │ │ ├                                     1   , 4
# │ │ │ ├                                     2   , 4
# │ │ │ ├                                     2   , 5
# │ │ │ ├                                     3   , 5
# │ │ │ ├─
# │ │ │ ×                                 = ( age , sid|pid|gid , name , age , sid , gid )
# │ │ │                                       18  , 1           , S_1  , 11  , 1   , 4
# │ │ │                                       18  , 1           , S_1  , 11  , 2   , 4
# │ │ │                                       18  , 1           , S_1  , 11  , 2   , 5
# │ │ │                                       18  , 1           , S_1  , 11  , 3   , 5
# │ │ │                                       18  , 2           , S_2  , 12  , 1   , 4
# │ │ │                                       18  , 2           , S_2  , 12  , 2   , 4
# │ │ │                                       18  , 2           , S_2  , 12  , 2   , 5
# │ │ │                                       18  , 2           , S_2  , 12  , 3   , 5
# │ │ │                                       18  , 3           , S_3  , 13  , 1   , 4
# │ │ │                                       18  , 3           , S_3  , 13  , 2   , 4
# │ │ │                                       18  , 3           , S_3  , 13  , 2   , 5
# │ │ │                                       18  , 3           , S_3  , 13  , 3   , 5
# │ │ │                                       18  , 4           , G<18 , 17  , 1   , 4
# │ │ │                                       18  , 4           , G<18 , 17  , 2   , 4
# │ │ │                                       18  , 4           , G<18 , 17  , 2   , 5
# │ │ │                                       18  , 4           , G<18 , 17  , 3   , 5
# │ │ │                                       18  , 5           , G=18 , 18  , 1   , 4
# │ │ │                                       18  , 5           , G=18 , 18  , 2   , 4
# │ │ │                                       18  , 5           , G=18 , 18  , 2   , 5
# │ │ │                                       18  , 5           , G=18 , 18  , 3   , 5
# │ │ ├─
# │ │ σ[#1>#4,#2=#6]                      = ( age , gid , name , age , sid , gid )
# │ │                                         18  , 4   , G<18 , 17  , 1   , 4
# │ │                                         18  , 4   , G<18 , 17  , 2   , 4
# │ ├─
# │ π[#5]                                 = ( sid )
# │                                           1
# │                                           2
# ├─
# elim                                    = ( sid )
#                                             1
#                                             2
```

### Expression $(3)$: Incorrect

$$
\mathrm{elim}\!\left(
    \pi_{\\#1}\!\left(
        \texttt{STUDENT}
        \bowtie_{\textcolor{red}{\\#1 = \\#1\ell}}
        \sigma_{\\#3 < 18}\!\left(\texttt{PERSON}\right)
    \right)
\right)
$$

```py
eliminate(project[1](STUDENT |join[1 |eq| -1]| select[3 |lt| AGE_OF_MAJORITY](PERSON)))
# ┌─
# │ ┌─
# │ │ ┌─
# │ │ ┤ ( sid , gid )                   = ( sid , gid )
# │ │ ┤                                     1   , 4
# │ │ ┤                                     2   , 4
# │ │ ┤                                     2   , 5
# │ │ ┤                                     3   , 5
# │ │ ╞═
# │ │ ├ ┌─
# │ │ ├ │ ( sid|pid|gid , name , age )  = ( sid|pid|gid , name , age )
# │ │ ├ │                                   1           , S_1  , 11
# │ │ ├ │                                   2           , S_2  , 12
# │ │ ├ │                                   3           , S_3  , 13
# │ │ ├ │                                   4           , G<18 , 17
# │ │ ├ │                                   5           , G=18 , 18
# │ │ ├ ├─
# │ │ ├ σ[#3<18]                        = ( sid|pid|gid , name , age )
# │ │ ├                                     1           , S_1  , 11
# │ │ ├                                     2           , S_2  , 12
# │ │ ├                                     3           , S_3  , 13
# │ │ ├                                     4           , G<18 , 17
# │ │ ├─
# │ │ × σ[#1=#1ℓ]                       = ( sid , gid , sid , name , age )
# │ │                                       1   , 4   , 1   , S_1  , 11
# │ │                                       2   , 4   , 2   , S_2  , 12
# │ │                                       2   , 5   , 2   , S_2  , 12
# │ │                                       3   , 5   , 3   , S_3  , 13
# │ ├─
# │ π[#1]                               = ( sid )
# │                                         1
# │                                         2
# │                                         2
# │                                         3
# ├─
# elim                                  = ( sid )
#                                           1
#                                           2
#                                           3
```

### Expression $(4)$: Incorrect

$$
\begin{aligned}
    &\mathrm{elim}\!\left(
        \pi_{\\#1}\!\left(
            \texttt{STUDENT}
        \right)
    \right) \\
    &- \mathrm{elim}\!\left(
        \pi_{\\#1}\!\left(
            \texttt{STUDENT}
            \bowtie_{\\#1 = \\#2\ell}
            \sigma_{\\#3 \geq 18}\!\left(\texttt{PERSON}\right)
        \right)
    \right)
\end{aligned}
$$

```py
eliminate(project[1](STUDENT))
|difference| eliminate(project[1](STUDENT |join[1 |eq| -2]| select[3 |ge| AGE_OF_MAJORITY](PERSON)))
# ┌─
# ┤ ┌─
# ┤ │ ┌─
# ┤ │ │ ( sid , gid )                     = ( sid , gid )
# ┤ │ │                                       1   , 4
# ┤ │ │                                       2   , 4
# ┤ │ │                                       2   , 5
# ┤ │ │                                       3   , 5
# ┤ │ ├─
# ┤ │ π[#1]                               = ( sid )
# ┤ │                                         1
# ┤ │                                         2
# ┤ │                                         2
# ┤ │                                         3
# ┤ ├─
# ┤ elim                                  = ( sid )
# ┤                                           1
# ┤                                           2
# ┤                                           3
# ╞═
# ├ ┌─
# ├ │ ┌─
# ├ │ │ ┌─
# ├ │ │ ┤ ( sid , gid )                   = ( sid , gid )
# ├ │ │ ┤                                     1   , 4
# ├ │ │ ┤                                     2   , 4
# ├ │ │ ┤                                     2   , 5
# ├ │ │ ┤                                     3   , 5
# ├ │ │ ╞═
# ├ │ │ ├ ┌─
# ├ │ │ ├ │ ( sid|pid|gid , name , age )  = ( sid|pid|gid , name , age )
# ├ │ │ ├ │                                   1           , S_1  , 11
# ├ │ │ ├ │                                   2           , S_2  , 12
# ├ │ │ ├ │                                   3           , S_3  , 13
# ├ │ │ ├ │                                   4           , G<18 , 17
# ├ │ │ ├ │                                   5           , G=18 , 18
# ├ │ │ ├ ├─
# ├ │ │ ├ σ[#3≥18]                        = ( sid|pid|gid , name , age )
# ├ │ │ ├                                     5           , G=18 , 18
# ├ │ │ ├─
# ├ │ │ × σ[#1=#2ℓ]                       = ( sid , gid , gid , name , age )
# ├ │ │                                       2   , 5   , 5   , G=18 , 18
# ├ │ │                                       3   , 5   , 5   , G=18 , 18
# ├ │ ├─
# ├ │ π[#1]                               = ( sid )
# ├ │                                         2
# ├ │                                         3
# ├ ├─
# ├ elim                                  = ( sid )
# ├                                           2
# ├                                           3
# ├─
# −                                       = ( sid )
#                                             1
```
