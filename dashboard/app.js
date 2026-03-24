class TelemetryDashboard {
    constructor() {
        this.historyBody = document.getElementById('historyBody');
        this.totalTasksEl = document.getElementById('totalTasks');
        this.activeAgentsEl = document.getElementById('activeAgents');
        this.refreshBtn = document.getElementById('refreshBtn');
        
        this.refreshBtn.addEventListener('click', () => {
            this.refreshBtn.textContent = 'SYNCING...';
            this.fetchData().then(() => {
                setTimeout(() => this.refreshBtn.textContent = 'FORCE_SYNC()', 500);
            });
        });
        
        this.init();
    }
    
    async init() {
        await this.fetchData();
        // Poll every 3 seconds for live tracking capabilities
        setInterval(() => this.fetchData(), 3000);
    }
    
    async fetchData() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            this.render(data);
        } catch (error) {
            console.error("Telemetry Sync Error:", error);
            this.historyBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: #f00;">ERROR: CONNECTION TO MOTHER_SHIP LOST</td></tr>`;
        }
    }
    
    render(data) {
        if (!data || data.length === 0) {
            this.historyBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: #888;">NO_TELEMETRY_FOUND</td></tr>`;
            return;
        }

        let html = '';
        const uniqueAgents = new Set();
        
        data.forEach(entry => {
            const date = new Date(entry.timestamp);
            const timeString = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;
            
            let statusClass = 'status-running';
            let statusText = String(entry.status).toUpperCase();
            
            if (entry.status === 'completed') statusClass = 'status-completed';
            else if (entry.status === 'failed') statusClass = 'status-failed';
            else statusText = 'BOOTING...'; // Graceful fallback
            
            uniqueAgents.add(entry.agent_id);
            
            html += `
                <tr>
                    <td>${timeString}</td>
                    <td>${entry.task_id}</td>
                    <td><span style="color:var(--text-main)">${entry.agent_id}</span></td>
                    <td class="${statusClass}">[${statusText}]</td>
                    <td style="color:var(--text-dim); font-size:0.8rem;">${entry.os_path}</td>
                </tr>
            `;
        });
        
        this.historyBody.innerHTML = html;
        this.totalTasksEl.textContent = data.length;
        this.activeAgentsEl.textContent = uniqueAgents.size;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TelemetryDashboard();
});
