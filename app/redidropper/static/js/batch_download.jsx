// Implements the UI for downloading batch files
//
//  Components used:
//
//      Page
//      BatchForm
//      BatchInput
//      BatchSummary

window.components = {};

var BatchInput = React.createClass({
    render: function() {
        var self = this;
        return(
            <div className="batch-input form-group">
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

var BatchForm = React.createClass({
    updateField: function(key, value) {
        var data = this.props.formData;
        data[key] = value;
        this.props.update(data);
    },
    render: function() {
        var self = this;
        var options = [
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
        return(
            <div id="batch-form" className='row'>
                <div className="col-sm-offset-3 col-sm-6">
                    <div className="form-horizontal">
                        {options.map(function (option, index) {
                            return (
                                <BatchInput key={index} options={option}/>
                            );
                        })}
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
    render: function() {
        return(
            <div id="batch-summary">
                summary: query = {this.props.query}
                <button
                    className='btn'
                    onClick={this.props.toggle.bind(this)}>Back</button>
            </div>
        );
    }
});


var Page = React.createClass({
    getInitialState: function() {
        return {
            activePanel: 0,
            formData: {},
            query: '',
        };
    },

    updateForm: function(data) {
        this.setState({
            formData: data,
            query: JSON.stringify(data)
        });
    },

    toggle: function() {
        this.setState({
            activePanel: this.state.activePanel === 0 ? 1 : 0
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
                        <BatchSummary toggle={this.toggle} query={this.state.query}/>
                    </div>
                </div>
        );
    }
});

React.render(<Page/>, document.getElementById("batch_download"));
