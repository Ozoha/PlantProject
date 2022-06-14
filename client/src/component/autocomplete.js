
import Autocomplete from '@mui/material/Autocomplete';
import * as React from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';




export default class ComponentAutoComplete extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      current_id: null,
      isLoaded: false,
      ids: []
    };
  }

  componentDidMount() {
    fetch("http://localhost:5000/ids")
      .then(res => res.json())
      .then(
        (ids) => {
          this.setState({
            isLoaded: true,
            ids: ids['ids'],
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      )
  }

  handleDelete(event, current_id) {
    if(window.confirm('Delete the item?')){
        const data = new FormData();
        data.append('current_id', this.state.current_id)
        fetch('http://localhost:5000/delete_id', {
          method: 'POST',
          body: data,
        })
        .then(response => response.json())
        .then(success => {
           const {error, isLoaded, ids} = this.state;
           const new_ids = ids.filter((id) => id !== this.state.current_id);
           this.setState({
              isLoaded: true,
              ids: new_ids
           });
           console.log(error)
           console.log(isLoaded)
        })
        .catch(error => console.log(error));
    }
  }
  save_id(event, current_id) {
    this.setState({
      current_id: current_id
    });
  }

  render() {
    const {error, isLoaded, ids} = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
//      <>
      <Autocomplete
          disablePortal
//          multiple
          id="combo-box-demo"
          options={ids}
          sx={{ width: 300 }}
          onChange={this.save_id.bind(this)}
          renderInput={(params) => <TextField {...params} label="ID"
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <Stack direction="row" spacing={1}>
                <Button className="btn btn-danger" variant="contained" color="primary" size="small"
                    onClick={this.handleDelete.bind(this)}
                    >
                    Delete
                </Button>
              </Stack>
            ),
          }}

        />}
      />
      );
    }
  }
}
