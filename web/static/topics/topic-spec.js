/**
 * Created by telvis on 11/7/14.
 */
describe("Controller: TopicCtrl", function(){
    beforeEach(module('topicApp'));
    var scope, window, controller, mockBackend, bootstrapped_results;

    beforeEach(inject(function($controller, $rootScope, $httpBackend){
        // Mock Bootstrapped data from templates/topics/topic.html
        bootstrapped_results= {
            'count' : 10,
            'topics' : [
                {
                    'phrase' : "test 1",
                    'bibleverse' : "test 1:1",
                    "search_url" : "http://localhost/biblestudy/?search=test"

                }
            ]
        };
        scope = $rootScope.$new();
        controller = $controller;
        window = {};
        window.HK = {};
        window.HK.results = bootstrapped_results;

        mockBackend = $httpBackend;
    }));

    it('creates a TopicCtl controller', function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });

    it('tests splitting the results list into 3 parts', function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        ret = ctrl.split_results_into_columns(undefined, 3);
        expect(ret).toEqual([[],[],[]]);

        ret = ctrl.split_results_into_columns(['one', 'two', 'three', 'four'], 3);
        expect(ret).toEqual([['one', 'four'],['two'],['three']]);
    });

    it("tests the scroll topic results query", function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
        var mock_response = {
            'topic_results': {
                'count' : 10,
                'topics' : [
                    {
                        'phrase' : "testing 2",
                        'bibleverse' : "test 1:2",
                        "search_url" : "http://localhost/biblestudy/?search=test2"

                    }
                ]
            }
        };

        expected_results = {
            'count' : 20,
            'topics' : [
                {
                    'phrase' : "test 1",
                    'bibleverse' : "test 1:1",
                    "search_url" : "http://localhost/biblestudy/?search=test"

                },
                {
                        'phrase' : "testing 2",
                        'bibleverse' : "test 1:2",
                        "search_url" : "http://localhost/biblestudy/?search=test2"

                }
            ]
        };

        mockBackend.expectPOST("/api/topics/").respond(200, mock_response);
        scope.scroll_action();
        mockBackend.flush();
        expect(scope.results).toEqual(expected_results);
    });

    it("tests the scroll topic results query error", function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
        mockBackend.expectPOST("/api/topics/").respond(400, '');
        scope.scroll_action();
        mockBackend.flush();
        expect(scope.results).toEqual(bootstrapped_results);
    });
});