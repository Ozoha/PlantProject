import React, { Component } from 'react'
import {DropzoneDialog} from 'material-ui-dropzone'
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';


export default class ComponentUploadFile extends Component {
    constructor(props) {
        super(props);
        this.state = {
            open: false,
            files: [],
            failed_docs: [],
            saved_docs: []
        };
    }

    handleClose() {
        this.setState({
            open: false
        });
    }

    handleSave(files) {
        const data = new FormData();
        for (let i = 0; i < files.length; i++) {
          data.append('files' + i, files[i])
        }
        this.setState({
            files: files,
            open: false
        });
        fetch(this.props.url, {
            method: 'POST',
            body: data,
            })
            .then(response => response.json())
            .then(success => {
            const { failed_docs, saved_docs } = success
                this.setState({
                    files: files,
                    open: false,
                    failed_docs: failed_docs,
                    saved_docs: saved_docs
                });
        })
        .catch(error => console.log(error));
    }

    handleOpen() {
        this.setState({
            open: true,
        });
    }

    render() {
        return (
            <div>
                <Button onClick={this.handleOpen.bind(this)}>
                  Add File
                </Button>
                <DropzoneDialog
                    open={this.state.open}
                    onSave={this.handleSave.bind(this)}
                    acceptedFiles={[".csv, text/csv, application/vnd.ms-excel, application/csv, text/x-csv, application/x-csv, text/comma-separated-values, text/x-comma-separated-values"]}
                    showPreviews={true}
                    maxFileSize={5000000}
                    filesLimit={100}
                    onClose={this.handleClose.bind(this)}
                />
                <ul>
                  {this.state.failed_docs.map(doc => (
                    <li key={doc}>
                       <Alert severity="error">

                       Failure! kit id: {doc}!
                       The reason of failure is not clear.
                       Could be on of:
                       1. Loading Sample/Taxonomy ID: {doc} already in DB.
                       2. Loading Taxonomy ID: {doc}  is missing from sample.
                       </Alert>
                    </li>
                  ))}
                </ul>
                <ul>
                  {this.state.saved_docs.map(doc => (
                    <li key={doc}>
                       <Alert severity="success">success! kit id: {doc}!</Alert>
                    </li>
                 ))}
                </ul>
            </div>
        );
    }
}
