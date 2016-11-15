function progressChart() {
  var width = 600;
  var height = 175;
  var domainMax = 20;
  var dotSize = 0.4; // diameter as % of color bar height

  var xPadding = 50;
  var yPadding = 15;
  var stages = ["Plan", "Build", "Test", "Reflect"];

  function chart(selection) {
    selection.each(function(entry, i) {
      var values = entry["values"].map(function(val, idx){
        val["idx"] = idx;
        return val;
      });

      /* scales */
      var x = d3.scaleLinear()
        .domain([0, domainMax + 1])
        .range([0, width]);

      var y = d3.scaleLinear()
        .domain([0, stages.length + 1])
        .range([height, 0]);

      /* data and positioning helpers */
      var getIndex = function(d) { return d["idx"] + 1; }
      var getStageValue = function(d) { return d["stage"]; };
      var isStudentPost = function(d) { return d["user_role"] == 1; };
      var giveX = function(d, i) { return x(getIndex(d)); };
      var giveY = function (d) { return y(getStageValue(d)); };

      /* svg */
      var vbx = width + 2 * xPadding;
      var vby = height + 2 * yPadding;

      var svg = d3.select(this)
        .append("svg")
        .classed("svg-content", true)
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 " + vbx + " " + vby);

      /* main padding group */
      var main = svg.append("g")
        .attr("transform", "translate(" + xPadding + ", " + yPadding + ")");

      /* color bars and totals */
      var histogram = d3.histogram()
        .domain(x.domain())
        .thresholds([1.5, 2.5, 3.5])
        .value(getStageValue);
      var bins = histogram(values.filter(isStudentPost));

      var dyText = -13;
      var xBar = x(0);
      var wBar = x.range()[1];
      var hBar = Math.abs(y(1) - y(0));
      var xSummary = xBar + wBar + 4;
      var wSummary = 30;

      // for each stage bar...
      stages.forEach(function(stage, idx) {
        var yBar = y(idx + 1.5);    // top edge of rect
        var yText = y(idx + 0.5);   // bottom edge of text
        var total = bins[idx].length;

        // bar group
        var group = main
          .append("g")
          .attr("class", "stage-" + stage.toLowerCase());

        // bar label
        group.append("text")
          .attr("text-anchor", "end")
          .attr("x", xBar)
          .attr("y", yText)
          .attr("dy", dyText)
          .attr("dx", -4)
          .text(stage);

        // bar
        group.append("rect")
          .attr("x", xBar)
          .attr("y", yBar)
          .attr("width", wBar)
          .attr("height", hBar)
          .attr("class", "colorbar");

        // summary block
        group.append("rect")
          .attr("x", xSummary)
          .attr("y", yBar)
          .attr("width", wSummary)
          .attr("height", hBar)
          .attr("class", "colorbar");

        // bar total
        group.append("text")
          .attr("text-anchor", "middle")
          .attr("x", xSummary + (wSummary / 2))
          .attr("y", yText)
          .attr("dy", dyText)
          .classed("summary", true)
          .text(total);
      });

      // top text
      main.append("text")
        .attr("text-anchor", "end")
        .attr("x", xSummary + wSummary)
        .attr("y", 10)
        .attr("dx", -2)
        .text("Totals:");

      // total posts
      main.append("text")
        .attr("text-anchor", "middle")
        .attr("x", xSummary + (wSummary / 2))
        .attr("y", y(0))
        .classed("summary", true)
        .text(values.filter(isStudentPost).length);

      main.append("text")
        .attr("text-anchor", "end")
        .attr("x", xSummary)
        .attr("y", y(0))
        .text("Total posts:");

      /* graph */
      // line
      var line = d3.line()
        .x(giveX)
        .y(giveY);

      // clipping rect
      var clip = main.append("clipPath")
        .attr("id", "graph-area")
        .append("rect")
        .attr("x", x(0))
        .attr("y", y(4.5))
        .attr("width", wBar)
        .attr("height", hBar * 4);

      // clipped group
      var group = main
        .append("g")
        .attr("clip-path", "url(#graph-area)");

      // inner group
      var group = group.append("g");

      // draw line
      group.append("path")
        .datum(values.filter(function(d){ return isStudentPost(d); }))
        .attr("d", line)
        .attr("class", "graphline");

      // draw circles
      group.selectAll("circle")
        .data(values)
        .enter()
        .filter(function (d) { return isStudentPost(d); })
        .append("circle")
        .attr("cx", giveX)
        .attr("cy", giveY)
        .attr("class", function (d) {
          var nameIdx = getStageValue(d) - 1;
          return "stage-" + stages[nameIdx].toLowerCase();
        })
        .attr("r", dotSize / 2 * hBar);

      // draw bars
      group.selectAll("line")
        .data(values)
        .enter()
        .filter(function (d) { return !isStudentPost(d); })
        .append("line")
        .attr("x1", giveX)
        .attr("y1", y(4.5))
        .attr("x2", giveX)
        .attr("y2", y(0.5))
        .attr("class", "mentorline");

      // shift left if necessary
      if (values.length > domainMax) {
        var offset = x(domainMax) - x(values.length);
        group.attr("transform", "translate(" + offset + ", 0)");
      }

    });
  }

  chart.width = function(value) {
    if (!arguments.length) return width;
    width = value;
    return chart;
  };

  chart.height = function(value) {
    if (!arguments.length) return height;
    height = value;
    return chart;
  };

  chart.domainMax = function(value) {
    if (!arguments.length) return domainMax;
    domainMax = value;
    return chart;
  };

  chart.dotSize = function(value) {
    if (!arguments.length) return dotSize;
    dotSize = value;
    return chart;
  };

  return chart;
}