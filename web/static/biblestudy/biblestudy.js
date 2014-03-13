/**
 * Created by telvis on 12/30/13.
 */


function BibleStudyCtrl($window, $scope, $log, $location, HkSearch){
    /* Controller for BibleStudy app */

    /* init search results obj */
    $scope.search_results = {};
    $scope.search_results.habakkuk_message = null;
    $scope.show_habakkuk_message = true;

    /* init pagination */
    $scope.pagination = {"start_enabled":"disabled",
                         "end_enabled":"disabled"}
    $scope.num_search_result_pages = _.range(1,2);

    /* init text search */
    $scope.search_params = { placeholder : "love, life, children",
                             text: $window.HK.search_text ? $window.HK.search_text : "",
                             start_date: null,
                             end_date: null,
                             date: null}

    // Init Bootstrapped Data
    $scope.popular_list = $window.HK.popular_list;
    $scope.search_results.results = $window.HK.search_results.results;
    $scope.search_results.count = $scope.search_results.results.length;
    $scope.search_results.total = $scope.search_results.results.length;
    $scope.search_results.habakkuk_message = $window.HK.search_results.habakkuk_message;
    $scope.search_results.date_str = $window.HK.search_results.date_str;


    $scope.gridOptions = {
        data: 'popular_list',
        columnDefs: [{field:'term', displayName:'Bible Reference'},
                     {field: 'count', displayName: 'Popularity'}],
        enableSorting: true,
        multiSelect: false,
        sortInfo: { fields: ['count', 'term'], directions: ['desc','asc'] }
    };


    $scope.search_action = function (){
        /* when 'Search!' is clicked */
        $log.info("[search_action] running search_action. got text: " + $scope.search_params.text);
        HkSearch.query($scope.search_params).then(function(d){
            $scope.search_results = d;
            $log.info("[search_action] running search_action. returned: " + $scope.search_results.count);
            if (d.path){
                $location.hash('');
                $location.search('search', $scope.search_params.text);
            }
        })
    }; // search action

    $scope.recommend_action = function(bibleverse){
        /* when a user clicks on a bibleverse in search results */
        $log.info("[recommend_action] - clicked: " + bibleverse);
        search_params = {'text': bibleverse};
        HkSearch.recommend(search_params).then(function(result){
            $scope.search_results = result;
            $log.info("[recommend_action] returned: "+ $scope.search_results.count);
        })
    };
}

function HkSearch($log, $http){
    /* angular service that handles $http lookups to the backend */
    var text_search_service = {};


    text_search_service.query = function(search_params){
        $log.info("[HkSearch.query] Searching backend for "+search_params.text);
        var promise = $http.get('/biblestudy/', {params: {search : search_params.text,
                                            format : 'json'}}
        ).then(this.search_success);
        return promise;
    };

    text_search_service.recommend = function(search_params){
        $log.info("[HkSearch.recommend] Searching backend for "+search_params.text)
        var promise = $http.get('/biblestudy/', {params: {r:search_params.text, format: 'json'}}
        ).then(this.recommend_success)
        return promise;
    };

    /* http search returned successfully */
    text_search_service.search_success = function(response){
        var data = response.data;
        $log.info("[search_success] - success yo! ");
        var search_results = {};
        search_results.results = data.search_results;
        search_results.count = data.search_results.length;
        search_results.total = data.search_results.length;
        search_results.habakkuk_message = "Here are search results for "+data.search_text;
        search_results.date_str = data.search_results.date_str;
        if (data.path){
            search_results.path = data.path;
        }


        return search_results;
    }

    /* http recommendation returned successfully */
    text_search_service.recommend_success = function(response){
        var data = response.data;
        $log.info("[search_success] - success yo! ");
        var search_results = {};
        search_results.results = data.search_results;
        search_results.count = data.search_results.length;
        search_results.total = data.search_results.length;
        search_results.habakkuk_message = "Here are recommendations results for "+data.search_text;
        search_results.date_str = data.search_results.date_str;


        return search_results;
    }

    // TODO: handle error cases
    function search_failed(data, status, headers, config){
        $log.error("[search_failed] - it failed yo!!!");
    }

    return text_search_service;
}

/* directive to change focus from input element when the
*  form submits
*  See: http://johan.driessen.se/posts/Using-an-AngularJS-directive-to-hide-the-on-screen-keyboard-on-submit*/
function handlePhoneSubmit(){
    return {
        link: function(scope, element, attrs, controller){
            var textFields = element.find('input');
            element.bind('submit', function() {
                textFields[0].blur();
            });
        } // factory obj
    };
}

/* define the 'search' service */
var bibleStudyModule = angular.module("bibleStudyApp", ['ngGrid']);
bibleStudyModule.factory('HkSearch', HkSearch);
bibleStudyModule.controller("BibleStudyCtrl", BibleStudyCtrl);
bibleStudyModule.directive("handlePhoneSubmit",handlePhoneSubmit);

bibleStudyModule.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
});