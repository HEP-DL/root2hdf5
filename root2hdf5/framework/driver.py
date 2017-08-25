from stevedore import driver

#TODO: Put in the failure callback so that if 
# you don't have larcv installed, it fails gracefully

def process(driver_name, file_names):
  mgr = driver.DriverManager(
    namespace='root2hdf5.plugins',
    name=driver_name,
    invoke_on_load=False,
  )
  mgr.driver.process(file_names)
