from unity_py.unity_exception import UnityException
from unity_py.resources.collection import Collection

import pytest

@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")

def test_read_corrupt_stac():
    with pytest.raises(UnityException):
        Collection.from_stac("tests/test_files/doesnt.exist")
    with pytest.raises(UnityException):
        collection = Collection.from_stac("tests/test_files/catalog_corrupt_02.json")
    with pytest.raises(UnityException):
        collection = Collection.from_stac("tests/test_files/catalog_corrupt.json")

def test_read_stac():
    collection = Collection.from_stac("tests/test_files/cmr_granules.json")
    assert collection.collection_id == "C2011289787-GES_DISC"
    datasets = collection._datasets
    assert len(datasets) == 2

    data_files = collection.data_locations()
    assert len(data_files) == 6
    data_files = collection.data_locations(["data","opendap"])
    assert len(data_files) == 4
    data_files = collection.data_locations(["data","opendap","metadata"])
    assert len(data_files) == 6
    data_files = collection.data_locations(["data"])
    assert len(data_files) == 2
    for x in data_files:
        assert x in ['https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2016/235/SNDR.SS1330.CHIRP.20160822T0005.m06.g001.L1_AQ.std.v02_48.G.200425095850.nc', 'https://data.gesdisc.earthdata.nasa.gov/data/CHIRP/SNDR13CHRP1.2/2016/235/SNDR.SS1330.CHIRP.20160822T0011.m06.g002.L1_AQ.std.v02_48.G.200425095901.nc']

        #Try a "classic" catalog + item files stac catalog
    collection = Collection.from_stac("tests/test_files/catalog_01.json")
    datasets = collection._datasets
    assert len(datasets) == 1
    data_files = collection.data_locations()
    assert len(data_files) == 2
    data_files = collection.data_locations(["data"])
    assert len(data_files) == 1
    data_files = collection.data_locations(["metadata_stac"])
    assert len(data_files) == 1
    assert data_files[0] == "/unity/ads/sounder_sips/chirp_test_data/SNDR.SS1330.CHIRP.20160829T2317.m06.g233.L1_AQ.std.v02_48.G.200425130422.json"


def test_write_stac():
    collection = Collection.from_stac("tests/test_files/cmr_granules.json")
    Collection.to_stac(collection, "tests/test_files" )


# for x in 4000:
#     dataset = Dataset(namne, start, stoptime)
#     dataset.addFile("data", "/path/to/tiled.nc")

# dataset.to_stac("ouput_file_location.json")
# def test_write_stac():
#     unity2stac("catalog.json")
#     assert True == True
