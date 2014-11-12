/**
 * Created by telvis on 11/7/14.
 */
describe("Controller: TopicCtrl", function(){
    beforeEach(module('topicApp'));
    var scope, window, controller;

    beforeEach(inject(function($controller, $rootScope){
        // Mock Bootstrapped data from templates/topics/topic.html
        scope = $rootScope.$new();
        controller = $controller;
        window = {};
        window.HK = {'results':{}};
    }));

    it('creates a TopicCtl controller', function(){
        var ctrl = controller('TopicCtrl', {$window: window, $scope: scope});
        expect(ctrl).toBeDefined();
    });
});