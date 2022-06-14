import React from "react";
import ComponentUploadFile  from "./uploadfile";
//import ComponentUploadFileTaxonomy  from "./uploadfiletaxonomy";
import ComponentAutoComplete  from "./autocomplete";
import AppBar from "@material-ui/core/AppBar";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import Box from "@material-ui/core/Box";

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return <div {...other}>{value === index && <Box p={3}>{children}</Box>}</div>;
}

export default function ComponentTabs() {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <>
      <AppBar position="static">
        <Tabs value={value} onChange={handleChange} centered>
          <Tab label="Upload Samples" />
          <Tab label="Upload Taxonomy" />
          <Tab label="Delete by ID" />
        </Tabs>
      </AppBar>
      <TabPanel value={value} index={0}>
        <ComponentUploadFile url='http://localhost:5000/upload_samples'/>
      </TabPanel>

      <TabPanel value={value} index={1}>
        <ComponentUploadFile url='http://localhost:5000/upload_taxonomy'/>
      </TabPanel>

      <TabPanel value={value} index={2}>
        <ComponentAutoComplete />
      </TabPanel>
    </>
  );
}