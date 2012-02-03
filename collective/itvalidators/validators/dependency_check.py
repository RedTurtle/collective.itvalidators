# -*- coding: utf-8 -*-

from Products.validation.interfaces.IValidator import IValidator
from collective.itvalidators import validatorsMessageFactory as _
from zope.i18nmessageid import Message
from Products.validation.i18n import recursiveTranslate
from Products.CMFCore.utils import getToolByName

class DependencyCheckValidator:
    """ 
    Validator for making a field required when another field is not giving a proper value

    Check that an "observedField" field value is "warnValue" or not.
    If it is, check also that the current field value is "wantedValue".

    >>> class D:
    ...     def __init__(self, observed, observator):
    ...         self.observed = observed
    ...         self.observator = observator
    ...
    >>> request = {'foo': 'goodvalue'}
    >>> d = D('foo', 'foo')
    >>> val = DependencyCheckValidator('observed', 'warn', 'foo')
    >>> val(d.observed, d, REQUEST=request)
    True


    You can use an empty (None) "warnValue" to check if the "observedField" field contains
    no value.
    
    You can also leave to None the "wantedValue", to check that the current field use no value.

    """

    __implements__ = (IValidator,)

    name = 'dependencycheckvalidator'

    def __init__(self, observedField, warnValue=None, wantedValue=None, errormsg=None):
        self.observedField = observedField
        self.warnValue = warnValue
        self.wantedValue = wantedValue
        self.errormsg = errormsg

    def __call__(self, value, instance, *args, **kwargs):
        
        kw={
           'here': instance,
           'object': instance,
           'instance': instance,
           'value': value,
           'observedField': self.observedField,
           'warnValue': self.warnValue,
           'wantedValue': self.wantedValue,
           'kwargs': kwargs,
           }
        
        form = kwargs['REQUEST'].form
        
        if form.get(self.observedField)!=self.warnValue:
            return True
        elif value==self.wantedValue:
            return True
        
        # We are here only when validation fails

        kw['observedField'] = instance.getField(self.observedField).widget.label
        kw['warnValue'] = self.warnValue or (self.warnValue is None and 'no')
        kw['warnValue'] = self.wantedValue or (self.wantedValue is None and 'no')
                
        if self.errormsg and type(self.errormsg) == Message:
            #hack to support including values in i18n message, too. hopefully this works out
            #potentially it could unintentionally overwrite already present values
            self.errormsg.mapping = kw
            return recursiveTranslate(self.errormsg, **kwargs)
        elif self.errormsg:
            # support strings as errormsg for backward compatibility
            return self.errormsg % kw
        else:
            msg = _(u'"$observedField" field has $warnValue value. This requires here $wantedValue value.',
                    mapping={'observedField': kw['observedField'], 'warnValue': self.warnValue,
                             'wantedValue': self.wantedValue})
            return recursiveTranslate(msg, **kwargs)

#validation.register(DependencyCheckValidator())
