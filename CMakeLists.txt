cmake_minimum_required(VERSION 2.8.3)
project(rwt_config_generator)

find_package(catkin REQUIRED
    COMPONENTS rospy
)

catkin_python_setup()

catkin_package(
  CATKIN_DEPENDS rospy
)
catkin_install_python(PROGRAMS src/convert_rviz.py 
                      DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})