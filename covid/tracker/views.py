import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64
import urllib.parse

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import CovidData

def index(request):
    """
    Home page view - displays search form and all states data
    """
    states = CovidData.objects.all()
    context = {
        'states': states,
        'total_states': states.count()
    }
    return render(request, 'tracker/index.html', context)

def search_state(request):
    """
    Search for specific state data and display chart
    """
    state = None
    state_data = None
    chart_image = None
    error_message = None
    
    if request.method == 'POST':
        state = request.POST.get('state', '').strip()
        
        if state:
            # Clean and format state name
            state = state.lower().capitalize()
            
            try:
                # Search for the state (case-insensitive)
                state_data = CovidData.objects.get(
                    state__iexact=state
                )
                
                # Generate chart
                chart_image = generate_chart(state_data)
                
            except CovidData.DoesNotExist:
                error_message = f"No data found for '{state}'. Please check the state name and try again."
                # Suggest similar states
                similar_states = CovidData.objects.filter(
                    state__icontains=state
                )[:3]
                if similar_states:
                    suggestions = [state.state for state in similar_states]
                    error_message += f" Did you mean: {', '.join(suggestions)}?"
        else:
            error_message = "Please enter a state name."
    
    # Get all states for the dropdown/suggestions
    all_states = CovidData.objects.all().order_by('state')
    
    context = {
        'state': state,
        'state_data': state_data,
        'chart_image': chart_image,
        'error_message': error_message,
        'all_states': all_states,
    }
    
    return render(request, 'tracker/chart.html', context)

def generate_chart(state_data):
    """
    Generate matplotlib chart for the given state data
    Returns base64 encoded image string
    """
    try:
        # Clear any previous plots
        plt.clf()
        plt.figure(figsize=(10, 6))
        
        # Data for plotting
        categories = ['Confirmed', 'Active', 'Recovered', 'Deaths']
        values = [
            float(state_data.confirmed),
            float(state_data.active),
            float(state_data.recovered),
            float(state_data.deaths),
        ]

        colors = ['green', 'blue', 'orange', 'red']
        
        # Create bar chart
        bars = plt.bar(categories, values, color=colors)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                    f'{value:,}', ha='center', va='bottom', fontweight='bold')
        
        # Customize chart
        plt.title(f'COVID-19 Data for {state_data.state}', fontsize=16, fontweight='bold')
        plt.xlabel('Case Types', fontsize=12)
        plt.ylabel('Number of Cases', fontsize=12)
        
        # Format y-axis to show values in thousands/millions
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_number(x)))
        
        # Add legend with rates
        legend_labels = [
            f'Confirmed: {state_data.confirmed:,}',
            f'Active: {state_data.active:,} ({state_data.active_rate}%)',
            f'Recovered: {state_data.recovered:,} ({state_data.recovery_rate}%)',
            f'Deaths: {state_data.deaths:,} ({state_data.death_rate}%)'
        ]
        
        # Create custom legend
        legend_elements = [mpatches.Patch(color=color, label=label) 
                          for color, label in zip(colors, legend_labels)]
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
        
        # Adjust layout to prevent clipping
        plt.tight_layout()
        
        # Save plot to BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        # Encode to base64 string
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        
        plt.close()  # Close the plot to free memory
        
        return graphic
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        return None

def format_number(num):
    """Format large numbers for display"""
    if num >= 1_000_000:
        return f'{num/1_000_000:.1f}M'
    elif num >= 1_000:
        return f'{num/1_000:.1f}K'
    return str(int(num))

def api_state_data(request, state):
    """
    API endpoint to get state data as JSON
    """
    try:
        state_data = get_object_or_404(CovidData, state__iexact=state)
        data = {
            'state': state_data.state,
            'confirmed': state_data.confirmed,
            'active': state_data.active,
            'recovered': state_data.recovered,
            'deaths': state_data.deaths,
            'recovery_rate': state_data.recovery_rate,
            'death_rate': state_data.death_rate,
            'active_rate': state_data.active_rate,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def all_states_data(request):
    """
    Display all states data in a table format
    """
    states = CovidData.objects.all().order_by('-confirmed')
    
    # Calculate totals
    total_confirmed = sum(state.confirmed for state in states)
    total_active = sum(state.active for state in states)
    total_recovered = sum(state.recovered for state in states)
    total_deaths = sum(state.deaths for state in states)
    
    context = {
        'states': states,
        'totals': {
            'confirmed': total_confirmed,
            'active': total_active,
            'recovered': total_recovered,
            'deaths': total_deaths,
        }
    }
    
    return render(request, 'tracker/all_states.html', context)