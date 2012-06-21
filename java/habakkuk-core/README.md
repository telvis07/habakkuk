This is the storm application for real-time analysis of religious tweets.

# To Build

    $ git clone proj.git
    $ cd habakkuk/java/habakkuk-core
    $ mvn compile
    $ mvn package

# To Run

    $ storm jar target/habakkuk-core-0.0.1-SNAPSHOT-jar-with-dependencies.jar technicalelvis.habakkuk.SimpleTopology username password
