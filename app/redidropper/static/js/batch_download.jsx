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
            <div className="batch-input">
                <input name={this.props.key}
                       type="text"
                       value={this.props.value}
                       onInput={function (event) {
                               console.log(event)
                               self.props.update.call(undefined, event.target.value);
                           }}
                />
            </div>
        );
    }
});

var BatchForm = React.createClass({
    updateField: function(key, value) {
        var data = this.props.formData;
        console.log(key, value)
        data[key] = value;
        this.props.update(data);
    },
    render: function() {
        var self = this;
        var keys = [
            'test'
        ];
        var funcs = keys.map(function(key) {
            return self.updateField.bind(self, key);
        });
        var values = keys.map(function(key) {
            return self.props.formData[key];
        });
        return(
            <div id="batch-form">
                {keys.map(function (key, index) {
                     return (
                         <BatchInput key={key} update={funcs[index]} value={values[index]}/>
                     )
                 })}
                <button onClick={this.props.toggle.bind(undefined)}>Finalize</button>
            </div>
        );
    }
});

var BatchSummary = React.createClass({
    render: function() {
        return(
            <div id="batch-summary">
                summary: query = {this.props.query}
                <button onClick={this.props.toggle.bind(undefined)}>Back</button>
            </div>
        );
    }
});


var Page = React.createClass({
    getInitialState: function() {
        return {
            activePanel: 0,
            formData: {
                test: undefined
            },
            query: '',
        };
    },

    updateForm: function(data) {
        this.setState({
            formData: data,
            query: JSON.stringify(data)
        });
        console.log(JSON.stringify(data));
    },

    toggle: function() {
        this.setState({
            activePanel: this.state.activePanel === 0 ? 1 : 0
        })
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
