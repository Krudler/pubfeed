import pytest
from pubfeed.pubdict import PubDict as pubd, PubVal, PubKey, AllPubKeys

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
    _ = numpub['one']

    assert get_result == 3 
    assert set_result == 4


def test_sub_to_multiple_keys(create_test_pubdicts):
    """
    Subscribe the same callable to multiple keys.
    """
    numpub, strpub, empub = create_test_pubdicts

    get_result = []
    set_result = []

    def on_set():
        nonlocal set_result
        set_result.append(4) 
    
    def on_get():
        nonlocal get_result
        get_result.append(3) 
     
    numpub.subtoset(['one', 'two','three'], on_set)
    numpub.subtoget(['one', 'two','three'], on_get)

    numpub['one'] = 2
    _ = numpub['one']
    
    numpub['two'] = 2
    _ = numpub['two']
    
    numpub['three'] = 2
    _ = numpub['three']

    assert get_result == [3,3,3] 
    assert set_result == [4,4,4]


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
    _ = numpub['one']

    assert get_result == 6
    assert set_result == 5 

def test_sub_to_getset(create_test_pubdicts):

    numpub, strpub, empub = create_test_pubdicts

    get_result = None
    set_result = None

    @numpub.subtogetandset('one')
    def set_vals():
        nonlocal get_result
        nonlocal set_result
        get_result = 'get'
        set_result = 'set'

    numpub['one'] = 1
    _ = numpub['one']

    assert get_result == 'get'
    assert set_result == 'set'

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

    @strpub.subtoget('one', call_order=0) 
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

    @numpub.subtoset('one', args=(3,))
    def multiply_one(x):
        nonlocal set_result
        set_result =  2 * x
    
    numpub['one']  = 'one'

    assert set_result == 6

def test_simple_kwargs(create_test_pubdicts):

    numpub, strpub, empub = create_test_pubdicts
    
    get_result = None

    @numpub.subtoget('one', kwargs={'x': 12, 'y':3})
    def multiply_two(x=1, y=1):
        nonlocal get_result
        get_result = x*y

    _ = numpub['one']

    assert get_result == 36


def test_substitute_args(create_test_pubdicts):
    """
    Should be able to specify when PubVal arguments should be passed to the subscribing
    callable. 
    """
    numpub, strpub, empub = create_test_pubdicts

    set_result = None
    get_result = None

    @numpub.subtoset('two', args=PubVal)
    def multiply_three(x):
        nonlocal set_result
        set_result = 3 * x

    numpub['two'] = 3

    assert set_result == 9

    @numpub.subtoset('one', args=(PubVal))
    def multiply_one(x):
        nonlocal set_result
        set_result =  2 * x
    
    numpub['one']  = 3

    assert set_result == 6

    @numpub.subtoget( 3 , kwargs={'x': PubKey, 'y':PubVal})
    def multiply_two(x=1, y=1):
        nonlocal get_result
        get_result = x*y

    numpub[3] = 4
    
    assert get_result == None
    
    _ = numpub[3]
    
    assert get_result == 12


def test_simple_sub_to_all_keys(create_test_pubdicts):
    """
    Subscribe a callable to all keys. When any key is set it should be squared and 
    replace the original value.  
    """

    numpub, strpub, empub = create_test_pubdicts
    set_results = []
    
    @numpub.subtoset(AllPubKeys)
    def square():
        nonlocal set_results
        set_results.append('x')
    
    numpub['one'] = 1
    numpub['two'] = 2
    numpub['three'] = 3

    assert set_results == ['x','x','x']


def test_replace_value(create_test_pubdicts):
    """
    When setting and retrieving values in the dict we might want to change them before 
    returning them. This can be used for a few things, including validating values before
    settings or changing them in some way before returning. 
    """
    numpub, strpub, empub = create_test_pubdicts

    @strpub.subtoset('one', replace_value=True)
    def  complete_replace():
        """
        No matter what the value is for this key the output will always be the same. 
        """

        return 'STATIC_OUTPUT'
    
    strpub['one'] = 'first value'

    assert strpub['one'] == 'STATIC_OUTPUT'

    @strpub.subtoget('two', args = PubVal, replace_value=True)
    def return_upper(x: str):
        """
        This function should replace the value with an uppercase version of the provided.
        """

        return x.upper()
    
    strpub['two'] = 'test value'

    assert strpub['two'] == 'TEST VALUE'


def test_sub_and_replace_to_all_keys(create_test_pubdicts):
    """
    Subscribe a callable to all keys. When any key is set it should be squared and 
    replace the original value.  
    """

    numpub, strpub, empub = create_test_pubdicts

    @numpub.subtoset(AllPubKeys, args=PubVal, replace_value=True)
    def square(x):
        return x * x
    
    numpub['one'] = 1
    numpub['two'] = 2
    numpub['three'] = 3

    assert numpub['one'] == 1
    assert numpub['two'] == 4
    assert numpub['three'] == 9