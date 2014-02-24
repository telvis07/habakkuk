/**
 * Created by telvis on 12/30/13.
 */


function BibleStudyCtrl($window, $scope, $log, HkSearch){
    /* methods */
    $scope.search_action = search_action;

    /* Controller for BibleStudy app */
    $scope.popular_list = {};
    $scope.popular_list_selected_item = null;

    /* init search results obj */
    $scope.search_results = {};
    $scope.search_results.habakkuk_message = null;
    $scope.show_habakkuk_message = true;

    /* init pagination */
    $scope.pagination = {"start_enabled":"disabled",
                         "end_enabled":"disabled"}
    $scope.num_search_result_pages = _.range(1,2);

    /* init text search */
    $scope.text_search = { placeholder : "love, christmas, chocolate",
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
    $scope.search_results.date = "Valentine's Day - February 14, 2013";


    $scope.gridOptions = {
        data: 'popular_list',
        columnDefs: [{field:'term', displayName:'Bible Reference'},
                     {field: 'count', displayName: 'Popularity'}],
        enableSorting: true,
        multiSelect: false,
        sortInfo: { fields: ['count', 'term'], directions: ['desc','asc'] }
    };


    function search_action(){
        /* when 'Search!' is clicked */
        $log.info("[search_action] running search_action. got text: " + $scope.text_search.text);
        HkSearch.query($scope.text_search).then(function(d){
            $scope.search_results = d;
            $log.info("[search_action] running search_action. returned: " + $scope.search_results.count);
        })

    }
}

function HkSearch($log, $http){
    /* angular service that handles $http lookups to the backend */
    var text_search_service = {};

    text_search_service.query = function(text_search){
        $log.info("[HkSearch.query] TODO: call $http with text "+text_search.text);
        var promise = $http.get('/biblestudy/', {params: {search : text_search.text,
                                            format : 'json'}}
        ).then(search_success);
        return promise;
    }

    function search_success(response){
        data = response.data;
        $log.info("[search_success] - success yo! " + JSON.stringify(data));
        var search_results = {};
        search_results.results = data.search_results;
        search_results.count = data.search_results.length;
        search_results.total = data.search_results.length;
        // $scope.search_results.habakkuk_message = $window.HK.search_results.habakkuk_message;
        search_results.date = "Not Valentine's Day - February 15, 2013";

        return search_results;
    }

    function search_failed(data, status, headers, config){
        $log.error("[search_failed] - it failed yo!!!");
    }

    return text_search_service;
}

/* define the 'search' service */
var bibleStudyModule = angular.module("bibleStudyApp", ['ngGrid']);
bibleStudyModule.factory('HkSearch', HkSearch);
bibleStudyModule.controller("BibleStudyCtrl", BibleStudyCtrl);