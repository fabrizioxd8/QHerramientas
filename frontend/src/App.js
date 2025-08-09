import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [tools, setTools] = useState([]);
  const [projects, setProjects] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [activeCheckouts, setActiveCheckouts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [toolForm, setToolForm] = useState({
    name: '', description: '', category: '', serial_number: '', location: ''
  });
  const [projectForm, setProjectForm] = useState({
    name: '', description: '', start_date: '', end_date: ''
  });
  const [workerForm, setWorkerForm] = useState({
    name: '', email: '', department: '', phone: ''
  });
  const [checkoutForm, setCheckoutForm] = useState({
    tool_id: '', project_id: '', worker_id: '', expected_return: ''
  });

  // Fetch data functions
  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const fetchTools = async () => {
    try {
      const response = await axios.get(`${API}/tools`);
      setTools(response.data);
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchWorkers = async () => {
    try {
      const response = await axios.get(`${API}/workers`);
      setWorkers(response.data);
    } catch (error) {
      console.error('Error fetching workers:', error);
    }
  };

  const fetchActiveCheckouts = async () => {
    try {
      const response = await axios.get(`${API}/checkouts/active`);
      setActiveCheckouts(response.data);
    } catch (error) {
      console.error('Error fetching active checkouts:', error);
    }
  };

  // Form submission handlers
  const handleAddTool = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/tools`, toolForm);
      setToolForm({ name: '', description: '', category: '', serial_number: '', location: '' });
      fetchTools();
      fetchDashboard();
    } catch (error) {
      console.error('Error adding tool:', error);
    }
    setLoading(false);
  };

  const handleAddProject = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/projects`, projectForm);
      setProjectForm({ name: '', description: '', start_date: '', end_date: '' });
      fetchProjects();
      fetchDashboard();
    } catch (error) {
      console.error('Error adding project:', error);
    }
    setLoading(false);
  };

  const handleAddWorker = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/workers`, workerForm);
      setWorkerForm({ name: '', email: '', department: '', phone: '' });
      fetchWorkers();
      fetchDashboard();
    } catch (error) {
      console.error('Error adding worker:', error);
    }
    setLoading(false);
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/checkout`, checkoutForm);
      setCheckoutForm({ tool_id: '', project_id: '', worker_id: '', expected_return: '' });
      fetchTools();
      fetchActiveCheckouts();
      fetchDashboard();
    } catch (error) {
      console.error('Error checking out tool:', error);
      alert('Error: ' + (error.response?.data?.detail || 'Failed to checkout tool'));
    }
    setLoading(false);
  };

  const handleReturn = async (checkoutId) => {
    setLoading(true);
    try {
      await axios.post(`${API}/return`, { checkout_id: checkoutId });
      fetchTools();
      fetchActiveCheckouts();
      fetchDashboard();
    } catch (error) {
      console.error('Error returning tool:', error);
    }
    setLoading(false);
  };

  // Initial data fetch
  useEffect(() => {
    fetchDashboard();
    fetchTools();
    fetchProjects();
    fetchWorkers();
    fetchActiveCheckouts();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'available': return 'text-green-600 bg-green-100';
      case 'checked_out': return 'text-blue-600 bg-blue-100';
      case 'in_maintenance': return 'text-yellow-600 bg-yellow-100';
      case 'needs_calibration': return 'text-orange-600 bg-orange-100';
      case 'lost': return 'text-red-600 bg-red-100';
      case 'damaged': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">Tool Room Manager</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['dashboard', 'tools', 'projects', 'workers', 'checkout', 'returns'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && dashboardData && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Dashboard Overview</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">T</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Total Tools</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.total_tools}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">A</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Available Tools</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.available_tools}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">O</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Checked Out</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.checked_out_tools}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">M</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">In Maintenance</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.maintenance_tools}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">P</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Active Projects</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.active_projects}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-semibold">W</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Total Workers</dt>
                          <dd className="text-lg font-medium text-gray-900">{dashboardData.total_workers}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Checkouts</h3>
                  <div className="overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tool</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Worker</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {dashboardData.recent_checkouts.map((item, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {item.tool_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {item.project_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {item.worker_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(item.checkout.checkout_date).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tools Tab */}
          {activeTab === 'tools' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-medium text-gray-900">Tools Management</h2>
              </div>

              {/* Add Tool Form */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Tool</h3>
                <form onSubmit={handleAddTool} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <input
                    type="text"
                    placeholder="Tool Name"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={toolForm.name}
                    onChange={(e) => setToolForm({ ...toolForm, name: e.target.value })}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Category"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={toolForm.category}
                    onChange={(e) => setToolForm({ ...toolForm, category: e.target.value })}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Serial Number"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={toolForm.serial_number}
                    onChange={(e) => setToolForm({ ...toolForm, serial_number: e.target.value })}
                  />
                  <input
                    type="text"
                    placeholder="Location"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={toolForm.location}
                    onChange={(e) => setToolForm({ ...toolForm, location: e.target.value })}
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:col-span-2"
                    value={toolForm.description}
                    onChange={(e) => setToolForm({ ...toolForm, description: e.target.value })}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Tool'}
                  </button>
                </form>
              </div>

              {/* Tools List */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Serial</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tools.map((tool) => (
                      <tr key={tool.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {tool.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tool.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tool.serial_number || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(tool.status)}`}>
                            {tool.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tool.location}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Projects Tab */}
          {activeTab === 'projects' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Projects Management</h2>

              {/* Add Project Form */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Project</h3>
                <form onSubmit={handleAddProject} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <input
                    type="text"
                    placeholder="Project Name"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={projectForm.name}
                    onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
                    required
                  />
                  <input
                    type="date"
                    placeholder="Start Date"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={projectForm.start_date}
                    onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
                    required
                  />
                  <input
                    type="date"
                    placeholder="End Date (Optional)"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={projectForm.end_date}
                    onChange={(e) => setProjectForm({ ...projectForm, end_date: e.target.value })}
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:col-span-2"
                    value={projectForm.description}
                    onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Project'}
                  </button>
                </form>
              </div>

              {/* Projects List */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">End Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {projects.map((project) => (
                      <tr key={project.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {project.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(project.status)}`}>
                            {project.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {project.start_date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {project.end_date || 'N/A'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {project.description || 'No description'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Workers Tab */}
          {activeTab === 'workers' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Workers Management</h2>

              {/* Add Worker Form */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Worker</h3>
                <form onSubmit={handleAddWorker} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <input
                    type="text"
                    placeholder="Worker Name"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={workerForm.name}
                    onChange={(e) => setWorkerForm({ ...workerForm, name: e.target.value })}
                    required
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={workerForm.email}
                    onChange={(e) => setWorkerForm({ ...workerForm, email: e.target.value })}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Department"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={workerForm.department}
                    onChange={(e) => setWorkerForm({ ...workerForm, department: e.target.value })}
                    required
                  />
                  <input
                    type="tel"
                    placeholder="Phone (Optional)"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={workerForm.phone}
                    onChange={(e) => setWorkerForm({ ...workerForm, phone: e.target.value })}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 sm:col-span-2 lg:col-span-4"
                  >
                    {loading ? 'Adding...' : 'Add Worker'}
                  </button>
                </form>
              </div>

              {/* Workers List */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {workers.map((worker) => (
                      <tr key={worker.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {worker.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {worker.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {worker.department}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {worker.phone || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Checkout Tab */}
          {activeTab === 'checkout' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Tool Checkout</h2>

              {/* Checkout Form */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Check Out Tool</h3>
                <form onSubmit={handleCheckout} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <select
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={checkoutForm.tool_id}
                    onChange={(e) => setCheckoutForm({ ...checkoutForm, tool_id: e.target.value })}
                    required
                  >
                    <option value="">Select Tool</option>
                    {tools.filter(tool => tool.status === 'available').map((tool) => (
                      <option key={tool.id} value={tool.id}>
                        {tool.name} - {tool.category}
                      </option>
                    ))}
                  </select>
                  <select
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={checkoutForm.project_id}
                    onChange={(e) => setCheckoutForm({ ...checkoutForm, project_id: e.target.value })}
                    required
                  >
                    <option value="">Select Project</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}
                  </select>
                  <select
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={checkoutForm.worker_id}
                    onChange={(e) => setCheckoutForm({ ...checkoutForm, worker_id: e.target.value })}
                    required
                  >
                    <option value="">Select Worker</option>
                    {workers.map((worker) => (
                      <option key={worker.id} value={worker.id}>
                        {worker.name} - {worker.department}
                      </option>
                    ))}
                  </select>
                  <input
                    type="date"
                    placeholder="Expected Return Date"
                    className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={checkoutForm.expected_return}
                    onChange={(e) => setCheckoutForm({ ...checkoutForm, expected_return: e.target.value })}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 sm:col-span-2 lg:col-span-4"
                  >
                    {loading ? 'Checking Out...' : 'Check Out Tool'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Returns Tab */}
          {activeTab === 'returns' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900">Active Checkouts & Returns</h2>

              {/* Active Checkouts List */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tool</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Worker</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Checkout Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Return</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {activeCheckouts.map((item) => (
                      <tr key={item.checkout.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {item.tool?.name || 'Unknown Tool'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.project?.name || 'Unknown Project'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.worker?.name || 'Unknown Worker'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(item.checkout.checkout_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.checkout.expected_return ? new Date(item.checkout.expected_return).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => handleReturn(item.checkout.id)}
                            disabled={loading}
                            className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          >
                            Return Tool
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;