#!/bin/bash
set -e
# ./manage.py jenkins

coverage run --source='.' manage.py test web topic_analysis
coverage report
karma start
