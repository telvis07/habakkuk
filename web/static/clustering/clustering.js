/* angular app to browse habakkuk clusters and facet results */

/* Controller for clustering visualization */
function HkClusterCtrl($window, $scope, $log){
     // clusters for queries
     $scope.facets = $window.HK.facets;
     $scope.unfiltered_clusters = $window.HK.clusters;
     $log.info("Got "+$scope.facets.length + " facets");
     $scope.clusters = filterClusters(null);
     $scope.clickedFacet =  clickedFacet;

     function clickedFacet(index){
         /* fires when ever a term is clicked in the facet counts panel */
         var selected_term = null;

         // de-select other terms
         // TODO: support multi-select
         for(var i=0; i<$scope.facets.length; i++){
             if(i==index){
                 continue;
             }
             $scope.facets[i].selected = false;
             $scope.facets[i].class = "";
         }

         // toggle selected flag
         var selected = !$scope.facets[index].selected;
         $scope.facets[index].selected = selected;

         if (selected){
           // highlight the row by changing 'class'
           $log.info("selected "+index+" from facets table");
           $scope.facets[index].class = "success";
           selected_term = $scope.facets[index].term;
         }else {
           $log.info("de-selected "+index+" from facets table");
           $scope.facets[index].class = "";
         }
         $scope.clusters = filterClusters(selected_term);
     };

     function filterClusters(term) {
        /* Remove cluster entries that do not contain 'term' */
        var data = $scope.unfiltered_clusters;
        var clusters = data.children;

        if (term === null){
            // No filters so return unfiltered list
            return $scope.unfiltered_clusters;
        }else{
            var _filtered = {name:"root", children:[]};
            // iterate over all clusters
            for (var i=0; i<clusters.length; i++){
                var cluster = clusters[i];
                var topics = cluster.children[0],
                    bibleverses = cluster.children[1];
                // iterate over all bibleverses in the cluster
                for (var j=0; j<bibleverses.children.length; j++){
                    var bv = bibleverses.children[j].name;
                    if (bv == term){
                        _filtered.children.push(cluster);
                        break;
                    }
                }
            }
            return _filtered;
        }
     };
  }

/* Directive to draw D3 cluster dengogram
 * See: http://bl.ocks.org/mbostock/4063570
 */
function HkDendogramDirective($log, $window) {
    var width = $(window).width() * 0.66;
         height = $(window).height();

      return {
        restrict: 'E',
        scope: {clusters:"="},
        link: function(scope, element, attrs){
           var cluster = d3.layout.cluster()
                .size([height, width - 160]);

           var diagonal = d3.svg.diagonal()
                .projection(function(d) { return [d.y, d.x]; });

           var svg = d3.select(element[0])
              .append("svg")
                .attr("width", width)
                .attr("height", height)
              .append("g")
                .attr("transform", "translate(40, 0)");

            scope.$watch('clusters', function(newVal, oldVal){
              if (newVal){
                $log.info("redrawing clusters")

                // remove so we can redraw
                svg.selectAll('*').remove();

                // convert json to array of nodes
                var nodes = cluster.nodes(newVal);
                // array of links from parent to child
                var links = cluster.links(nodes);

                // add the links
                _link = svg.selectAll(".link")
                    .data(links)
                    .enter()
                    .append("path")
                      .attr("class", "link")
                      .attr("d", diagonal);

                // add the nodes
                var node = svg.selectAll(".node")
                  .data(nodes)
                .enter().append("g")
                  .attr("class", "node")
                  .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

                // add circle per node
                node.append("circle")
                  .attr("r", 4.5);

                // add text per node
                node.append("text")
                  .attr("dx", function(d) { return d.children ? -8 : 8; })
                  .attr("dy", 3)
                  .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
                  .text(function(d) { return d.name; });
              } // if (data)
            }); // watch
        }
    };
}

var clusterModule = angular.module("clusterApp",[]);
clusterModule.controller('ClusterCtrl', HkClusterCtrl);
clusterModule.directive('hkukClustersViz', HkDendogramDirective);