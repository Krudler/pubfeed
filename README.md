# pubfeed
A simple package for python sub/pub patterns.

## Motivation

An easy and lightweight way to implement a pub/sub pattern and create lightweight pipelines using familiar dictionary-like affordances.

## Installation

```cmd
pip install pubfeed 
```

## Usage

Some simple examples of executing callables. For a more comprehensive look at what can be done refer to ./pubfeed/tests/test_PubDict.py. 

### Basic usage

``` python

# Import the pubdcit object 
from pubfeed.pubdict import PubDict as pubd, PubVal

# Create a PubDict

pb  = pubd()

# Add/remove elements to the PubDict like a dictionary
pb['one'] = 1
pb['two'] = 2
pb[3] = 'three'

pb['two']

>> 2

# Print 'Ahoy' any time a value is set for the key 'two' 

pb.subtoset('two', lambda x: print('Ahoy'))

pb['two'] = 3

>> Ahoy

# As above, but with a decorator

@pb.subtoset('two')
def print_ahoy():
    print('Ahoy')

pb['two'] = 4

>> Ahoy

# Print a capitalized version value when a value is set for the key 'one'
# Specifying args=PubVal passes the value being set to the subscribing function

@pb.subtoset('one', args=PubVal)
def print_cap(val):
    print(val.upper())

pb['one'] = 'allcaps'
>> ALLCAPS

pb['one']
>> allcaps
```