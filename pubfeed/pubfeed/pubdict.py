from collections import defaultdict
from typing import Any, Iterable, Hashable, Union, Callable, Optional


class PubVal(object):
    """
    An object representing the published value. 
    """
    def __class__(self):
        return 'PubVal'


class PubKey(object):
    """
    An object representing the published key.
    """
    pass


class AllPubKeys(object):
    """
    An object representing all published keys in a PubDict object. The rule 
    will be that any callables subscribed to AllPubKeys will be run first, 
    then all callables for specific keys will be run. 
    """
    pass


class PubDictException(Exception):
    """
    Exceptions for PubDict.
    """
    pass


class PubDict(dict):
    """
    A dictionary that can publish get and set events to subscribed callables.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._subs_to_sets = defaultdict(list)
        self._subs_to_all_sets = []
        self._subs_to_gets = defaultdict(list)
        self._subs_to_all_gets = []


    def subtoget(self, 
                 keys: Union[Iterable[Hashable], Hashable, AllPubKeys],
                 func: Callable = None,
                 args: Optional[Union[str, tuple]] = None,
                 kwargs: Optional[dict] = None,
                 replace_value: bool = False,
                 call_order: Optional[int] = None,
    ) -> None:
        """
        Subscribe a callable to a get key. Every time a value is retrieved for the key 
        the following the callable will be executed.  
        """

        def decorator_sub(func) -> None:
            self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['get'], replace_value=replace_value, call_order=call_order)  

        if not func:
            return decorator_sub
        
        self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['get'], replace_value=replace_value, call_order=call_order)  


    def subtoset(self, 
                 keys: Union[Iterable[Hashable], Hashable, AllPubKeys],
                 func: Callable = None,
                 args: Optional[Union[str, tuple]] = None,
                 kwargs: Optional[dict] = None,
                 replace_value: bool = False,
                 call_order: Optional[int] = None,
    ) -> None:
        """
        Subscribe a callable to a set function.
        """

        def decorator_sub(func) -> None:
            self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['set'], replace_value=replace_value, call_order=call_order)  

        if not func:
            return decorator_sub
        
        self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['set'], replace_value=replace_value, call_order=call_order)  

    def subtogetandset(self, 
                 keys: Union[Iterable[Hashable], Hashable, AllPubKeys],
                 func: Callable = None,
                 args: Optional[Union[str, tuple]] = None,
                 kwargs: Optional[dict] = None,
                 replace_value: bool = False,
                 call_order: Optional[int] = None,
    ) -> None:
        """
        Subscribe to both get and set events for the dictionary. 
        """

        def decorator_sub(func) -> None:
            self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['get','set'], replace_value=replace_value, call_order=call_order)  

        if not func:
            return decorator_sub
        
        self._sub(keys=keys, func=func, args=args, kwargs=kwargs, on_events=['get','set'], replace_value=replace_value, call_order=call_order)  


    def _sub(self, *args, **kwargs) -> None: 
        """
        Not for direct use. This method adds a subscriber for the specified event. 
        """
        kwargs['publisher'] = self
        subscriber = PubDictSubscriber(*args, **kwargs)

        pub_map = {
            'get': (self._subs_to_gets, self._subs_to_all_gets),
            'set': (self._subs_to_sets, self._subs_to_all_sets)
        }

        for on_event in subscriber.on_events:
            if AllPubKeys in subscriber.keys:
                sub_index = 1
            else:
                sub_index = 0

            if sub_index:
                if isinstance(subscriber.call_order, int):
                    pub_map[on_event][sub_index].insert(subscriber.call_order, subscriber)
                else:
                    pub_map[on_event][sub_index].append(subscriber)
            else:
                for key in subscriber.keys:
                    if isinstance(subscriber.call_order, int):
                        pub_map[on_event][sub_index][key].insert(subscriber.call_order, subscriber)
                    else:
                        pub_map[on_event][sub_index][key].append(subscriber)

    def _pub(self, pub_key, pub_val, pub_qs):
        """
        Not for direct use. Publishes the key and value to the subscribers in the pub_qs.
        Also handles the replacing of values if the subscriber specifies that the value 
        should be replaced. Note that this method does not handle the order of the 
        callables, that's handled by the ques themselves. 
        """
    
        for q in pub_qs:
            for subscriber in q:
                sub_output = subscriber.run_func(pub_key, pub_val)
                if subscriber.replace_value:
                    pub_val = sub_output

        return pub_val


    def __getitem__(self, __key: Any) -> None:
        r = super().__getitem__(__key)
        
        pub_qs = []
        if self._subs_to_all_gets: pub_qs.append(self._subs_to_all_gets)
        if __key in self._subs_to_gets: pub_qs.append(self._subs_to_gets[__key])
        if pub_qs: 
            return self._pub(__key, r, pub_qs)

        return r


    def __setitem__(self, __key: Any, __value: Any) -> None:
        # r = super().__setitem__(__key, __value)
        pub_qs = []
        if self._subs_to_all_sets: pub_qs.append(self._subs_to_all_sets)
        if __key in self._subs_to_sets: pub_qs.append(self._subs_to_sets[__key])
        if pub_qs: 
            return super().__setitem__(__key, self._pub(__key, __value, pub_qs))       

        return super().__setitem__(__key, __value)


class PubDictSubscriber(object):
    """
    This class is for not for direct use. This class holds information about 
    the subscriber including how it should handle the execution of the 
    subscribing callable and the associated arguments. While this class holds 
    information on the order it should be executed it does not manage 
    execution order.
    """

    def __init__(self,
                 keys: Union[Iterable[Hashable], Hashable, AllPubKeys],
                 func: Callable,
                 args: Optional[Union[str, tuple]] = None,
                 kwargs: Optional[dict] = None,
                 replace_value: bool = False,
                 on_events: Union[str, list[str]] = None,
                 call_order: Optional[int] = None,
                 publisher: PubDict = None
        ):

        self.keys = [keys] if isinstance(keys, (Hashable, AllPubKeys)) else keys
        self.func = func
        self.args = self._validate_args(args) 
        self.kwargs = kwargs if kwargs else {}
        self.replace_value = replace_value
        self.on_events = [on_events] if isinstance(on_events, str) else on_events
        self.call_order = call_order
        self.publisher = publisher

    def _validate_args(self, args: Union[tuple[any], str, None]):
        if not args:
            return tuple()
        if isinstance(args, tuple):
            return args
        else:
            try:
                return tuple(args)
            except TypeError:
                return tuple([args])

    def run_func(self, pub_key: Hashable, pub_val: any):
        run_args = self._substitute_args(pub_key, pub_val, self.args) if self.args else self.args
        run_kwargs = self._substitute_args(pub_key, pub_val, self.kwargs) if self.kwargs else self.kwargs
        return self.func(*run_args, **run_kwargs)
    
    def _substitute_args(self, pub_key: Hashable, pub_val: any, args: Union[tuple, dict]) -> Union[tuple, dict]:
        
        if isinstance(args, tuple):
            out_args = []
            for arg in args:
                if arg is PubVal:
                    out_args.append(pub_val)
                elif arg is PubKey:
                    out_args.append(pub_key)
                else:
                    out_args.append(arg)

            out_args = tuple(out_args)

        if isinstance(args, dict):
             out_args = {}
             for k, v in args.items():
                if v is PubVal:
                    out_args[k] = pub_val
                elif v is PubKey:
                    out_args[k] = pub_key
                else:
                    out_args[k] = v
        
        return out_args