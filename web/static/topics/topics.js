/**
 * Created by telvis on 11/3/14.
 */

function TopicCtrl($window, $scope, $log, $http){
    $scope.busy = false;
    $scope.results = [];
    $scope.offset = 10;
    $scope.topic_name = null;

    var split_results_into_columns = function(result_list, num_columns)
    {
        /* Split topics results in to `num_columns` columns*/
        $log.info("in split_results_into_columns");

        var split_results_list = [];
        var idx;

        for (i=0; i<num_columns; i++){
            split_results_list.push([]);
        }

        if (!result_list){
            /* case when result_list is empty */
            return split_results_list;
        }

        for (i = 0; i < result_list.length; i++) {
            idx = i % num_columns;
            split_results_list[idx].push(result_list[i]);
        }

        return split_results_list;
    };

    $scope.scroll_action = function(){
        /* Call the POST api to fetch more results if the user scrolls */
        if ($scope.busy) return;
        $scope.busy = true;
        /* Hit the POST api to get phrases for scrolling */
        $log.info("[scroll_action] start");
        var params = {size: 10, offset:$scope.offset};
        var url = '/api/topics/';

        // the topic name is the entry in the url path.
        if ($scope.results.topic_name != null){
            url = url + $scope.results.topic_name;
        }

        $http.post(url, params)
            .success(function(response){
                $log.info("[HkTopicScroll.on_success]");
                var topic_results =response.topic_results;
                for (i=0; i<topic_results.topics.length; i++){
                    $scope.results.topics.push(topic_results.topics[i]);
                }

                $scope.results.count += topic_results.count;
                $scope.result_columns = split_results_into_columns($scope.results.topics, 2);
                $scope.offset += topic_results.count;
                $scope.busy = false;
            }).error(function(response){
                $log.info("[HkTopicScroll.on_failure]");
                $scope.offset += 10;
                $scope.busy = false;

            });
    };

    this.split_results_into_columns = split_results_into_columns;
    $scope.results = $window.HK.results;
    $scope.result_columns = split_results_into_columns($scope.results.topics, 2);
}

var topicModule = angular.module("topicApp", ['infinite-scroll']).config(function($httpProvider) {
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
});

topicModule.controller("TopicCtrl", TopicCtrl);