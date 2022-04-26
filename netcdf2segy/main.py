import sys

import netCDF4

from netcdf2segy.variable_dataset import VariableDataset3d


def convert_netcdf_variable(netcdf_dataset, variable_key):

    variable_dataset = VariableDataset3d(netcdf_dataset,
                                         ('x', 'y', 'z'),
                                         variable_key)

    print("variable_dataset =", variable_dataset)
    print("num_inlines =", variable_dataset.num_inlines())
    print("num_crosslines =", variable_dataset.num_xlines())
    print("max_num_trace_samples =", variable_dataset.max_num_trace_samples())
    print("num_traces =", variable_dataset.num_traces())


def convert_netcdf_dataset(netcdf_dataset, segy_filepath_base):
    """
    Args:
        netcdf_dataset: The input netCDF4.Dataset object.

        segy_filepath_base: The path to the SEG-Y output files. The last component
            of this path will be used as the prefix for the SEG-Y filenames.
    """
    variable_names = netcdf_dataset.variables.keys() - netcdf_dataset.dimensions.keys()
    for variable_key in variable_names:
        convert_netcdf_variable(netcdf_dataset, variable_key)


def convert_netcdf_file(netcdf_filepath, segy_filepath_base):
    """
    Args:
        netcdf_filepath: The path to the netCDF input file.

        segy_filepath_base: The path to the SEG-Y output files. The last component
            of this path will be used as the prefix for the SEG-Y filenames.
    """
    with netCDF4.Dataset(netcdf_filepath) as netcdf_dataset:
        convert_netcdf_dataset(netcdf_dataset, segy_filepath_base)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    netcdf_filepath = argv[0]
    segy_filepath_base = argv[1]

    convert_netcdf_file(netcdf_filepath, segy_filepath_base)

    return 0

if __name__ == '__main__':
    sys.exit(main())
