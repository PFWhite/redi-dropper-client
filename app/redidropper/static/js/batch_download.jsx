// Implements the UI for downloading batch files
//
//  Components used:
//
//      Page
//      BatchForm
//      BatchInput
//      BatchSummary

window.staticData = {
    dateHeading: 'Image Upload Date',
    dateHelpText: 'Images uploaded before the start date or after the end date will not be selected.',
    takenDateHeading: 'Image Taken Date',
    takenDateHelpText: 'Images taken before the start date or after the end date will not be selected.',
    subjectHeading: 'Subject ID',
    subjectHelpText: 'Select multiple by using the shift or the control or command key. ALL selects all subjects.',
    eventHeading: 'Redcap Events',
    eventHelpText: 'Select multiple by using the shift or the control or command key. ALL selects all events.',
};

var BatchInput = React.createClass({
    render: function() {
        var self = this;
        return(
            <div className="batch-input col-sm-12">
                <label className="col-sm-4 control-label" for={this.props.options.mykey}>
                    { this.props.options.display }
                </label>
                <div className="col-sm-8">
                    <input name={this.props.options.key}
                        className="form-control"
                        type={this.props.options.type}
                        value={this.props.options.value}
                        onChange={function (event) {
                                self.props.options.update.call(this, event.target.value);
                            }}
                    />
                </div>
            </div>
        );
    }
});

var BatchSelect = React.createClass({
    selectedString: function (option) {
        return option.selected ? 'selected="selected"' : '';
    },
    render: function() {
        var selecteds = this.props.options.filter(function (item) {
            return item.selected;
        }).map(function (item) {
            return item.value;
        });
        return (
        <div className="batch-select col-sm-12">
            <select id="" name="" multiple="multiple"
                    value={selecteds}
                    onChange={this.props.change}>
            {this.props.options.map(function (option) {
                return (
                <option value={option.value} >{option.display}</option>
                );
            })}
            </select>
        </div>
        );
    }
});

var BatchFormGroup = React.createClass({
    render: function() {
        return (
            <div className="form-group batch-form-group">
                <div className="col-sm-12">
                    <h3 className="batch-form-group-heading">
                        <strong>{this.props.heading}</strong>
                    </h3>
                    <p>
                        {this.props.helpText}
                    </p>
                </div>
                {this.props.selectOptions ? (
                    <BatchSelect change={this.props.change} options={this.props.selectOptions}/>
                    ) : ''
                }
                {this.props.options ? this.props.options.map(function (option, index) {
                    return (
                        <BatchInput key={index} options={option}/>
                    );
                }) : ''}
            </div>
        );
    }
});

var BatchForm = React.createClass({
    updateField: function(key, value) {
        var data = this.props.formData;
        data[key] = value;
        this.props.update(data);
    },
    updateSelect: function(key, event) {
        var data = this.props.formData;
        data[key] = [].map.call(event.target.selectedOptions, function (item) {
            return item.value
        });
        this.props.update(data);
    },
    getInitialState: function () {
        return {
            subjects: ['ALL'],
            events: ['ALL'],
        }
    },
    checkSelected: function(key, value) {
        return ( this.props.formData[key] || [] ).indexOf(value) > -1;
    },
    componentWillMount: function() {
        var self = this,
            queryParams = ['per_page=1000'].join('&');
        $.getJSON(window.origin + '/api/list_local_subjects?' + queryParams, function(data) {
            var subjects = data.data.list_of_subjects.map(function(item) {return item.redcap_id});
            subjects.sort().unshift('ALL');
            self.setState({
                subjects: subjects
            });
        });
        $.getJSON(window.origin + '/api/list_events', function(data) {
            var events = data.data.events.map(function(item) {return item.redcap_event});
            events.sort().unshift('ALL');
            self.setState({
                events: events
            });
        });
    },
    render: function() {
        var self = this;

        var subjectKey = 'subjects';
        var subjectChange = self.updateSelect.bind(self, subjectKey);
        var subjectOptions = self.state.subjects.map(function (item) {
            return {
                value: item,
                display: item,
                selected: self.checkSelected(subjectKey, item)
            };
        });
        var eventKey = 'events';
        var eventChange = self.updateSelect.bind(self, eventKey);
        var eventOptions = self.state.events.map(function (item) {
            return {
                value: item,
                display: item,
                selected: self.checkSelected(eventKey, item)
            };
        });
        var dateOptions = [
            {
                key: 'startDate',
                value: self.props.formData.startDate,
                type: 'date',
                update: self.updateField.bind(self, 'startDate'),
                display: 'Start Date'
            },
            {
                key: 'endDate',
                value: self.props.formData.endDate,
                type: 'date',
                update: self.updateField.bind(self, 'endDate'),
                display: 'End Date'
            },
        ];

        var takenDateOptions = [
            {
                key: 'takenStartDate',
                value: self.props.formData.takenStartDate,
                type: 'date',
                update: self.updateField.bind(self, 'takenStartDate'),
                display: 'Start Date'
            },
            {
                key: 'takenEndDate',
                value: self.props.formData.takenEndDate,
                type: 'date',
                update: self.updateField.bind(self, 'takenEndDate'),
                display: 'End Date'
            },
        ];

        return(
            <div id="batch-form" className='row'>
                <div className="col-sm-offset-2 col-sm-8">
                    <div className="form-horizontal">

                        <BatchFormGroup heading={window.staticData.subjectHeading}
                                        selectOptions={subjectOptions}
                                        change={subjectChange}
                                        helpText={window.staticData.subjectHelpText}/>

                        <BatchFormGroup heading={window.staticData.eventHeading}
                                        selectOptions={eventOptions}
                                        change={eventChange}
                                        helpText={window.staticData.eventHelpText}/>

                        <BatchFormGroup heading={window.staticData.dateHeading}
                                        options={dateOptions}
                                        helpText={window.staticData.dateHelpText}/>

                        <BatchFormGroup heading={window.staticData.takenDateHeading}
                                        options={takenDateOptions}
                                        helpText={window.staticData.takenDateHelpText}/>
                        <button
                            className='btn'
                            onClick={this.props.toggle.bind(this)}>Finalize</button>
                    </div>
                </div>
            </div>
        );
    }
});

var BatchSummary = React.createClass({
    download: function(data) {
        var url = window.location.origin + '/api/batch_download?q=' + data;
        window.location = url;
    },
    render: function() {
        var uploadStart = this.props.formData.startDate || 'the beginning of time',
            uploadEnd = this.props.formData.endDate || 'present day',
            takenStart = this.props.formData.takenStartDate || 'the beginning of time',
            takenEnd = this.props.formData.takenEndDate || 'present day';

        return(
            <div id="batch-summary">
                <p className="summary-group">
                    The following subjects' data will be included in your batch:
                        {' ' + this.props.formData.subjects.join(',') + '.'}
                </p>
                <p className="summary-group">
                    The following events' data will be included in your batch:
                        {' ' + this.props.formData.events.join(', ') + '.'}
                </p>
                <p className="summary-group">
                    The files downloaded will have been uploaded from {uploadStart} to {uploadEnd}.
                </p>
                <p className="summary-group">
                    The files downloaded will have been created from {takenStart} to {takenEnd}.
                </p>
                <button
                    className='btn batch-finalize'
                    onClick={this.props.toggle.bind(this)}>Edit Batch</button>
                <button
                    className='btn batch-finalize'
                    onClick={this.download.bind(this, this.props.query)}>Download</button>
            </div>
        );
    }
});


var Page = React.createClass({
    getInitialState: function() {
        var formData = window.location.hash.slice(1,window.location.hash.length);
        formData = formData || '{"subjects":["ALL"],"events":["ALL"]}';
        return {
            activePanel: 0,
            formData: JSON.parse(formData),
            query: formData,
        };
    },

    updateForm: function(data) {
        var query = JSON.stringify(data);
        window.location.hash = '#' + query;
        this.setState({
            formData: data,
            query: query
        });
    },

    toggle: function() {
        var activePanel = this.state.activePanel === 0 ? 1 : 0;
        this.setState({
            activePanel: activePanel
        });
    },

    render: function() {
        var batchFormClasses = 'panel' + ( this.state.activePanel === 0 ? ' active' : '' ),
            batchSummaryClasses = 'panel' + ( this.state.activePanel === 1 ? ' active' : '' );
        return(
                <div id='batch-page'>
                    <h2>container</h2>
                    <div className={batchFormClasses}>
                        <BatchForm toggle={this.toggle} update={ this.updateForm } formData={this.state.formData}/>
                    </div>
                    <div className={batchSummaryClasses}>
                        <BatchSummary toggle={this.toggle} query={this.state.query} formData={this.state.formData}/>
                    </div>
                </div>
        );
    }
});

React.render(<Page/>, document.getElementById("batch_download"));
