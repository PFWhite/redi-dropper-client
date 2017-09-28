// Goal: Implement the simple navigation between tabs
//
//  Subject > Files
//
// Components used:
//
//      __1 SubjectsList
//      __2 FilesUpload
//      __3 NavController

// var Utils, React, $;

// ============ __1 SubjectsList
var SubjectsList = React.createClass({
    getInitialState: function() {
        return {
            list_of_subjects: null
        };
    },

    componentWillMount: function() {
        // this.updateSubjectsList('');
    },

    updateSubjectsList: function(subject_name) {
        var _this = this;
        var url = "/api/find_subject";
        var request = Utils.api_post_json(url, {name: subject_name});
        request.success( function(json) {
            _this.setState({
                list_of_subjects: json.data.subjects
            });
        });
        request.fail(function (jqXHR, textStatus, error) {
            console.log('Failed: ' + textStatus + error);
        });
    },

  subjectChanged: function() {
    var subject_name = this.refs.subject_name.getDOMNode().value.trim();
    if (subject_name.length > 0) {
        this.updateSubjectsList(subject_name);
    }
    else {
        this.setState(this.getInitialState());
    }
  },

  render: function() {
    var rows = [];
    var _this = this;

    var search_results_table;

    if (this.state.list_of_subjects === undefined) {
        //@TODO: show a "loading" animation
    }
    else if (this.state.list_of_subjects === null) {
        search_results_table = <div></div>
    }
    else if (this.state.list_of_subjects.length === 0) {
        search_results_table = <div>No subjects found.</div>;
    }
    else {
        this.state.list_of_subjects.map(function(record, i) {
            // Wire the click on the button to the parent
            // function subjectSelected() with the parameter record
            // which allows the parent component to access record data
            var selectSubject = _this.props.subjectSelected.bind(null, record);
            rows.push(
                <tr>
                    <td>
                        <button className="btn btn-lg2 btn-primary"
                            onClick={selectSubject}>
                            Select subject: {record}
                        </button>
                    </td>
                  </tr>
            );
        });

        search_results_table = (
        <div className="table-responsive">
            <table id="subject-table" className="table borderless">
                <thead>
                    <tr>
                        <th> Search Results </th>
                    </tr>
                </thead>
                <tbody id="subject-table-body">
                   {rows}
                </tbody>
            </table>
        </div>
        );
    }

    return (
    <div>
        <div className="form-group">
            <input className="form-control"
                    ref="subject_name"
                    onChange={this.subjectChanged}
                    placeholder="Please enter the REDCap Subject ID to search"
                    type="text" />
        </div>
        {search_results_table}
    </div>
    );
  }
});

// ============ __2 FilesUpload
var FilesUpload = React.createClass({
    // Note: This component has access to the
    //      subject_id
    // values shared by the NavController component

    getInitialState: function() {
        return {};
    },
    componentWillMount: function() {
        var self = this;
        var resumable = Utils.get_resumable_instance();
        resumable.setExtraData({
            'subject_id': self.props.subject_id
        });

        resumable.on('complete', function() {
            console.log("Uploaded byte count: " + resumable.getSize());
            $("#upload-complete-button").show();
        });

        resumable.on('uploadStart', function() {
            $("#upload-complete-button").hide();
        });
    },
    render: function() {
        return (
                <div className="table-responsive" >
                </div>
               );
    }
});


// ============ __3 NavController
var NavController = React.createClass({
    getInitialState: function() {
        //Add Listener for the url change
        window.onhashchange = this.urlChanged;

        var tabs = [
            "Subjects",
            "Files"
        ];
        return {
            current_tab: 0,
            tabs: tabs,
            subject_id: ""
        };
    },
    changeTab: function(i) {
        this.setState({
          current_tab: i
        });
    },
    subjectSelected: function(subject_id) {
        this.setState({
            current_tab: 1,
            subject_id: subject_id
        });
    },
    showFiles: function() {
        this.setState({current_tab: 2});
    },
    urlChanged: function () {
      var hash_value = location.hash;
      var current_tab = this.state.current_tab;

      //check whether the current state is not equal to hash value
      if("#" + this.state.tabs[current_tab] !== hash_value) {
        //State has to be changed
        if(hash_value === "#Subjects") {
          this.setState({
              current_tab: 0,
              subject_id: 0,
              eventEntity: ""
          });
        }
      }
    },
    render: function() {
        var visible_tab;
        var selected_subject_id = "";
        var breadcrumbs = [];
        var current_tab = this.state.current_tab;
        var tabs = this.state.tabs;

        for(var i = 0; i < tabs.length; i++) {
            var tab_class;
            if(current_tab === i) {
                breadcrumbs.push(<li><a>{tabs[i]}</a></li>);
            }
            else if(current_tab > i) {
                breadcrumbs.push(
                        <li className="prev-page" onClick={this.changeTab.bind(null, i)}>
                        <a>{tabs[i]}</a>
                        </li>);
            }
            else if(current_tab < i) {
                breadcrumbs.push(<li className="next-page"><a>{tabs[i]}</a></li>);
            }
        }

        $("#upload-files").hide();
        $("#upload-complete-button").hide();

        if(current_tab === 0) {
            window.location.hash = 'Subjects';
            // By passing the "subjectSelected" function to the SubjectsList component
            // we are allowing the SubjectsList component to execute it when
            // it is time to change the visible tab
            visible_tab = <SubjectsList subjectSelected = {this.subjectSelected} />;
        }
        else if(current_tab === 1) {
            selected_subject_id = "Subject ID: " + this.state.subject_id;
            window.location.hash = 'Files';
            $("#upload-files").show();
            $("#files-list").empty();

            // pass data to Resumable object so we can map files to the subject
            visible_tab = <FilesUpload showFiles = {this.showFiles}
                subject_id = {this.state.subject_id}
            />;
        }

        return (
            <div>
                <div className="panel-heading">
                    <div id="crumbs">
                        <ul>
                            {breadcrumbs}
                        </ul>
                    </div>
                </div>
                <div className="row">
                <div className="col-md-offset-4 col-md-4 col-xs-12">
                <table id="technician-table" className="table borderless">
                    <thead>
                    <tr>
                        <th>{selected_subject_id}</th>
                     </tr>
                </thead>
                </table>
                </div>
                </div>
                <div className="panel-body">
                    {visible_tab}
                </div>
            </div>
        );
    }
});

React.render(<NavController/>, document.getElementById("start-upload"));
