"""Provides the Analysis related classes."""
from .base import Base
from pathlib import Path
from functools import partial

class Analysis:
    _fields_ = ['dataset_id', 'description', 'name',  'predictions',
                'predictors', 'private', 'runs']
    _aliased_methods_ = ['delete', 'bundle', 'compile', 'full', 'resources']

    def __init__(self, *, analyses, name, dataset_id, **kwargs):
        self.name = name
        self.dataset_id = dataset_id
        self._analyses = analyses

        # Set up
        for k, v in kwargs.items():
            if k in set(self._fields_):
                setattr(self, k, v)

        # Create
        self._fromdict(self._analyses.post(**self._asdict()))

        ## Attach aliased methods
        for method in self._aliased_methods_:
            setattr(self,
                    method,
                    partial(
                        getattr(self._analyses, method),
                        self.hash_id)
                    )

    def _asdict(self):
        """ Return dictionary representation of valid fields """
        di = {}
        for field in self._fields_:
            if hasattr(self, field):
                di[field] = getattr(self, field)

        return di

    def _fromdict(self, di):
        """ Update field values from response """
        for k, v in di.items():
            setattr(self, k, v)

    def push(self):
        """ Push changes from to API, and sync with returned results"""
        self._fromdict(self._analyses.put(self.hash_id, **self._asdict()))

    def pull(self):
        """ Pull updates from API, overriding changes made locally """
        self._fromdict(self._analyses.get(self.hash_id))

    def get_status(self):
        """ Get and update compiled status """
        new_status = self._analyses.status(self.hash_id)
        self._fromdict(new_status)
        return new_status

    def clone(self):
        pass


class Analyses(Base):
    _base_path_ = 'analyses'
    _auto_methods_ = ('get', 'post')

    def put(self, id, **kwargs):
        """ Put analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self._client._put(self._base_path_, id=id, **kwargs)

    def delete(self, id):
        """ Delete analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self._client._delete(self._base_path_, id=id)

    def bundle(self, id, filename=None):
        """ Get analysis bundle
        :param str id: Analysis hash_id.
        :param str, object filename: Optional filename to save bundle to
        :return: client response object
        """
        bundle = self.get(id=id, sub_route='bundle')
        if filename is not None:
            if isinstance(filename, str):
                filename = Path(filename)
            with filename.open('wb') as f:
                f.write(bundle)
        else:
            return bundle

    def clone(self, id):
        """ Clone analysis
        :param str id: Analysis hash_id.
        :return: client response object, with new analysis id
        """
        return self.post(id=id, sub_route='clone')

    def create_analysis(self, *, name, dataset_id, **kwargs):
        return Analysis(analyses=self, name=name,
                        dataset_id=dataset_id, **kwargs)

    def compile(self, id):
        """ Submit analysis for complilation
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.post(id=id, sub_route='compile')

    def full(self, id):
        """ Get full analysis object (including runs and predictors)
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='full')

    def resources(self, id):
        """ Get analysis resources
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='resources')

    def status(self, id):
        """ Get analysis status
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='status')
