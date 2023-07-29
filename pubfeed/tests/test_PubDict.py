import pytest
from pubfeed.pubdict import PubDict as pubd, PubVal, PubKey

@pytest.fixture
def create_test_pubdicts():
    return [
        pubd([('one',1),('two',2),('three',3)]),
        pubd({'one':'one', 'two':'two', 'three':'three'}),
        pubd()
    ]

def test_create(create_test_pubdicts):
    """
    Creating a new PubDict object. Should behave just like a dictionary when 
    being created or used. 
    """
    numpub, strpub, empub = create_test_pubdicts

    assert isinstance(numpub, pubd)
    assert isinstance(strpub, pubd)
    assert isinstance(empub, pubd)


def test_basic_method_sub(create_test_pubdicts):
    """
    Test basic sub.
    """
    numpub, strpub, empub = create_test_pubdicts

    get_result = None
    set_result = None

    def on_set():
        nonlocal set_result
        set_result = 4 
    
    def on_get():
        nonlocal get_result
        get_result = 3 
     
    numpub.subtoset('one', on_set)
    numpub.subtoget('one', on_get)

    numpub['one'] = 2
    r = numpub['one']

    assert get_result == 3 
    assert set_result == 4


def test_basic_wrap_sub(create_test_pubdicts):
    """
    Testing basic subscriptions with wrappers.
    """
    numpub, strpub, empub = create_test_pubdicts

    get_result = None
    set_result = None

    @numpub.subtoset('one')
    def on_set():
        nonlocal set_result
        set_result =  5

    @numpub.subtoget('one') 
    def on_get():
        nonlocal get_result
        get_result = 6
    
    numpub['one'] = 2
    r = numpub['one']

    assert get_result == 6
    assert set_result == 5 

def test_sequence_sub(create_test_pubdicts):
    """
    Because more than one subscription can be added to a key we may want to
    specify in which order those subscriptions should be run. 
    """    
    numpub, strpub, empub = create_test_pubdicts

    get_results = []
    set_results = []

    @strpub.subtoset('one', call_order=1)
    def second_on_set():
        nonlocal set_results
        set_results.append('second')
    
    @strpub.subtoget('one', call_order=1)
    def second_on_get():
        nonlocal get_results
        get_results.append('second')

    @strpub.subtoset('one', call_order=0)
    def first_on_set():
        nonlocal set_results
        set_results.append('first')

    @strpub.subtoget('one', exec_order=0) 
    def first_on_get():
        nonlocal get_results
        get_results.append('first')
    
    strpub['one'] = 2
    _ = strpub['one']


    assert get_results == ['first','second'] 
    assert set_results == ['first','second']

def test_simple_args(create_test_pubdicts):
    """
    Providing additional ordered arguments when subscribing a callable to a key.
    """
    numpub, strpub, empub = create_test_pubdicts

    set_result = None
    get_result = None

    @numpub.subtoset('one', args=(3))
    def multiply_one(x):
        nonlocal set_result
        set_result =  2 * x
    
    numpub['one']  = 'one'

    assert set_result == 6

    @numpub.subtoget('one', kwargs={'x': 12, 'y':3})
    def multiply_two(x=1, y=1):
        nonlocal get_result
        get_result = x*y

    assert get_result == 36

def test_substitute_args(create_test_pubdicts):
    """
    Providing additional ordered arguments when subscribing a callable to a key.
    """
    numpub, strpub, empub = create_test_pubdicts

    set_result = None
    get_result = None

    @numpub.subtoset('one', args=(PubVal))
    def multiply_one(x):
        nonlocal set_result
        set_result =  2 * x
    
    numpub['one']  = 'one'

    assert set_result == 6

    @numpub.subtoget( 3 , kwargs={'x': PubKey, 'y':PubVal})
    def multiply_two(x=1, y=1):
        nonlocal get_result
        get_result = x*y

    numpub[3] = 4
    
    assert get_result == None
    
    _ = numpub[3]
    
    assert get_result == 12
