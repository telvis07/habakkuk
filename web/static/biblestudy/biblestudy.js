/**
 * Created by telvis on 12/30/13.
 */


function BibleStudyCtrl($window, $scope, $log, HkSearch){
    /* methods */
    $scope.search_action = search_action;

    /* Controller for BibleStudy app */
    $scope.search_text = null;
    $scope.popular_list = {};
    $scope.popular_list_selected_item = null;
    $scope.habakkuk_message = null;
    $scope.search_results = [];
    $scope.show_habakkuk_message = true;
    $scope.pagination = {"start_enabled":"disabled",
                         "end_enabled":"disabled"}
    $scope.num_search_result_pages = _.range(1,2);

    // search
    $scope.text_search = { placeholder : "love, christmas, chocolate",
                           text: "",
                           start_date: null,
                           end_date: null,
                           date: null}

    // Testing...
    $scope.popular_list = $window.HK.popular_list;
    $scope.search_results = $window.HK.search_results;
    $scope.search_results_count = $scope.search_results.length;
    $scope.total_search_results_count = $scope.search_results.length;
    $scope.habakkuk_message = $window.HK.habakkuk_message;

    $scope.gridOptions = {
        data: 'popular_list',
        columnDefs: [{field:'term', displayName:'Bible Reference'},
                     {field: 'count', displayName: 'Popularity'}],
        enableSorting: true,
        multiSelect: false,
        sortInfo: { fields: ['count', 'term'], directions: ['desc','asc'] }
    };

    function search_action(){
        $log.info("[search_actino] running search_action. got text: " + $scope.text_search.text);
        HkSearch.query($scope.text_search);
    }
}

function HkSearch($log){
    /* angular service that handles $http lookups to the backend */
    var text_search_service = {};
    text_search_service.query = function(text_search){
        $log.info("[TextSearchService] TODO: call $http with text "+text_search.text)
    }
    return text_search_service;
}

/* define the 'search' service */
var bibleStudyModule = angular.module("bibleStudyApp", ['ngGrid']);
bibleStudyModule.factory('HkSearch', HkSearch);
bibleStudyModule.controller("BibleStudyCtrl", BibleStudyCtrl);