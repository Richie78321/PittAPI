Pitt API
========

|Build Status| |License GPLv2| |Python >= 3.6|

Made by Ritwik Gupta at the University of Pittsburgh in an effort to get
more open data from Pitt.

Usage examples
--------------

.. code:: python

    from PittAPI import course, dining, lab, laundry, library, news, people, shuttle, textbook, ratemyprofessors

    ### Courses
    # Will return a list of dictionaries containing courses in subject
    cs_subject = course.get_term_courses(term='2194', subject='CS')
    cs_course = cs_subject['1501']
    cs_section_list = cs_course.sections
    big_dict = cs_section_list[0].to_dict()

    ### Textbook
    # Will return a list of dictionaries containing textbooks for a class
    # term number comes from pitt.verbacompare.com
    small_dict = textbook.get_textbook(term="3150", department="CS", course="445", instructor="RAMIREZ")
    
    ### Library
    # Will return a dictionary containing results from query
    big_dict = library.get_documents(query="computer")
    
    ### News
    # Will return a list of dictionaries containing news from main news feed
    medium_dict = news.get_news()

    ### Laundry
    # Will return a dictionary with amount of washers and dryers
    # in use vs. total washers and dryers at building
    small_dict = laundry.get_status_simple(building_name="TOWERS")

    ### Computer Lab
    # Will return a dictionary with status of the lab, and amount
    # of machines with a certain OS
    small_dict = lab.get_status(lab_name="ALUMNI")
    
    ### Shuttle
    # Will return a list of dictionaries containing routes of shuttles
    big_dict = shuttle.get_routes()
    
    ### People
    # Will return a list of people based on the query
    list_of_peeps = people.get_person(query="Smith")

    ### Dining
    # Will return a dictionary of dictionaries containing each dining location,
    # with its name, its open/closed status, and open times (if it exists)
    medium_dict = dining.get_locations()
    medium_dict = dining.get_locations_by_status(status="open")
    medium_dict = dining.get_locations_by_status(status="closed")
    # Will return a single dictionary of a dining location,
    # with its name, its open/closed status, and open times (if it exists)
    one = dining.get_location_by_name("taco_bell-schenley_cafe")
    two = dining.get_location_by_name("cup_&_chaucer-hillman")
    
    ### Rate My Professors
    # Will return a list of dictionaries containing the requested fields for
    # the professors that matched the query
    medium_dict = ratemyprofessors.get_rmp_by_name(prof_name="Joe Smith")
    # Will return a single dictionary (or None if no match) containing the
    # requested fields of the professor with a matching ID
    small_dict = ratemyprofessors.get_rmp_by_id(prof_id="9338")

Tests
-----

| Run tests with
  ``python3 -m "nose" --with-coverage --cov PittAPI/ --with-timer tests/*``.
| If your ``python -v`` is 3+, replace ``python3`` with ``python``.

License
-------

This project is licensed under the terms of the `GPLv2
license <LICENSE>`__.

.. |Build Status| image:: https://travis-ci.org/Pitt-CSC/PittAPI.svg?branch=master
   :target: https://travis-ci.org/Pitt-CSC/PittAPI
.. |License GPLv2| image:: https://img.shields.io/badge/license-GPLv2-blue.svg
   :target: LICENSE
.. |Python >= 3.6| image:: https://img.shields.io/badge/python-%3E%3D%203.6-green

