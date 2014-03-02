/**
 * Created by telvis on 1/8/14.
 */
describe("Controller: BibleStudyCtrl", function() {
    // Load the module, which contains the controller
    beforeEach(module('bibleStudyApp'));
    var scope, window, controller;

    beforeEach(inject(function($controller, $rootScope){
        scope = $rootScope.$new();
        controller = $controller;
        window = {};
        window.HK = {};
        window.HK.search_results = {};
        window.HK.search_results.results = [];
        window.HK.search_results.habakkuk_message = "testing";
    }));

    it('creates a BibleStudyCtrl controller', function(){
        var ctrl = controller('BibleStudyCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });

    it('verifies default scope values', function(){
        var ctrl = controller('BibleStudyCtrl', {$window: window, $scope: scope});
        expect(scope.search_results.results).toEqual([]);
        expect(scope.search_results.count).toEqual(0);
        expect(scope.search_results.total).toEqual(0);
        expect(scope.search_results.habakkuk_message).toEqual("testing");
        expect(scope.gridOptions).toBeDefined();
        expect(scope.search_params).toBeDefined();
        expect(scope.show_habakkuk_message).toBe(true);
        expect(scope.pagination).toEqual({"start_enabled":"disabled",
                         "end_enabled":"disabled"});
        expect(scope.num_search_result_pages).toEqual(_.range(1,2));
    });
});

describe("Service: HkSearch", function(){
    beforeEach(module('bibleStudyApp'));
    var scope, service, mockBackend, expected_response;

    beforeEach(inject(function($httpBackend, $rootScope, HkSearch){
        scope = $rootScope.$new();
        // this is a mock backend to control the
        // requests and responses from the server
        expected_response = {habakkuk_message: "Hello World!",
                     search_text: "love",
                     search_results: [
                        {
                            text: "Charity suffereth long, and is kind; charity envieth not; charity vaunteth not itself, is not puffed up,",
                            translation: "KJV",
                            bibleverse_human: "i_corinthians 13:4",
                            bibleverse: "i_corinthians 13:4"
                        }]
                    };
        mockBackend = $httpBackend;
        service = HkSearch;

    }));

    it('creates a HkSearch service', function(){
        expect(service).toBeDefined();
    });

    it('it tests the http search query', function(){
        expect(service).toBeDefined();
        spyOn(service, 'search_success').andCallThrough();
        var text_search = {text: "love"};
        mockBackend.expectGET("/biblestudy/?format=json&search=love").
            respond(expected_response);
        service.query(text_search);
        mockBackend.flush();
        expect(service.search_success).toHaveBeenCalled();
    });

    it('it tests the http recommend query', function(){
        expect(service).toBeDefined();
        spyOn(service, 'recommend_success').andCallThrough();
        var text_search = {text: "galatians 3:28"};
        mockBackend.expectGET("/biblestudy/?format=json&r=galatians+3:28").
            respond(expected_response);
        service.recommend(text_search);
        mockBackend.flush();
        expect(service.recommend_success).toHaveBeenCalled();
    });
});