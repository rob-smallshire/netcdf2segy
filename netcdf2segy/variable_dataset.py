from collections import namedtuple

from segpy.catalog import RowMajorCatalog2D
from segpy.dataset import Dataset

DimensionKeys = namedtuple('DimensionKeys', ['inline', 'xline', 'trace_sample'])

NUMBER_BASIS = 1  # One-based indexing

class VariableDataset3d(Dataset):
    """Adapts a netCDF variable to the Segy Dataset interface."""

    def __init__(self, netcdf_dataset, netcdf_dimension_keys, netcdf_variable_key):
        """
        Args:
            netcdf_dataset: The netCDF4.Dataset from which samples will
                be extracted.

            netcdf_dimension_keys: The keys corresponding to the three
                spatial dimensions, ordered to correspond with the inline,
                crossline and trace axes of the SEG-Y, where the inline number
                varies slowest and the trace sample number varies quickest. For example,
                ('x', 'y', 'z') would give north-south oriented inlines (constant
                x-value per inline), east-west oriented crosslines (constant
                y-value per crossline) and vertical traces.
        """
        self._netcdf_dataset = netcdf_dataset

        if len(netcdf_dimension_keys) != 3:
            raise ValueError("netcdf_dimension_keys {!r} does not contain exactly three items."
                             .format(netcdf_dimension_keys))

        for index, dimension_key in enumerate(netcdf_dimension_keys):
            if dimension_key not in netcdf_dataset.dimensions.keys():
                raise ValueError("netcdf_dimension_keys[{index}] == {key} is not one of {dimensions}"
                                 .format(index=index,
                                         key=dimension_key,
                                         dimensions=', '.join(netcdf_dataset.dimensions.keys())))

        if netcdf_variable_key not in netcdf_dataset.variables.keys():
            raise ValueError("netcdf_variable_key {} is not one of {}"
                             .format(netcdf_variable_key,
                                     ', '.join(netcdf_dataset.variables.keys())))
        self._netcdf_variable_key = netcdf_variable_key
        self._netcdf_variable = netcdf_dataset.variables[netcdf_variable_key]

        if self._netcdf_variable.ndim != 3:
            raise ValueError("netCDF variable {} has {} dimensions, not three"
                             .format(self._netcdf_variable_key,
                                     self._netcdf_variable.ndim))

        for dimension_key in netcdf_dimension_keys:
            if dimension_key not in self._netcdf_variable.dimensions:
                raise ValueError("{dimension} not a dimension of {variable}"
                                 .format(dimension=dimension_key,
                                         variable=self._netcdf_variable_key))

        self._netcdf_dimension_keys = DimensionKeys(*netcdf_dimension_keys)

        self._catalog = RowMajorCatalog2D(
            i_range=range(NUMBER_BASIS, self.num_inlines() + NUMBER_BASIS),  # TODO: One-based? Check!
            j_range=range(NUMBER_BASIS, self.num_xlines() + NUMBER_BASIS),   # TODO: One-based? Check!
            constant=0
        )

    def __repr__(self):
        return "{}({}({!r}), {!r}, {!r})".format(
            self.__class__.__name__,
            self._netcdf_dataset.__class__.__name__,
            getattr(self._netcdf_dataset, 'filepath', ''),
            self._netcdf_dimension_keys,
            self._netcdf_variable_key)

    # Begin Dataset Interface
    #
    # This portion of the interface is necessary for writing the SEG-Y data.

    @property
    def textual_reel_header(self):
        raise NotImplementedError

    @property
    def binary_reel_header(self):
        raise NotImplementedError

    @property
    def extended_textual_header(self):
        raise NotImplementedError

    @property
    def dimensionality(self):
        return self._netcdf_variable.ndim

    def trace_header(self, trace_index):
        raise NotImplementedError

    def trace_indexes(self):
        """Generate valid trace indexes """
        return range(0, self.num_traces())

    def trace_samples(self, trace_index, start=None, stop=None):
        raise NotImplementedError

    def num_traces(self):
        return self.num_inlines() * self.num_xlines()

    # End Dataset Interface

    def num_inlines(self):
        """The number of distinct inlines."""
        inline_dimension_index = self._netcdf_variable.dimensions.index(self._netcdf_dimension_keys.inline)
        return self._netcdf_variable.shape[inline_dimension_index]

    def num_xlines(self):
        """The number of distinct crosslines."""
        xline_dimension_index = self._netcdf_variable.dimensions.index(self._netcdf_dimension_keys.xline)
        return self._netcdf_variable.shape[xline_dimension_index]

    def max_num_trace_samples(self):
        """The maximum number of samples per trace."""
        trace_sample_dimension_index = self._netcdf_variable.dimensions.index(self._netcdf_dimension_keys.trace_sample)
        return self._netcdf_variable.shape[trace_sample_dimension_index]

    def inline_xline_numbers(self):
        return iter(self._catalog)

    def trace_index(self, inline_xline):
        """Obtain the trace_samples index given an inline and an xline.

        Note:
            Inline and crossline numbers should not be
            relied upon to be zero- or one-based indexes (although
            they may be).

        Args:
            inline_xline: A 2-tuple of inline number, crossline number.

        Returns:
            A trace_samples index which can be used with trace_samples().
        """
        return self._catalog[inline_xline]
