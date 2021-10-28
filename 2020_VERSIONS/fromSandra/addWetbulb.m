function [wetSound,errorTracker] = addWetbulb(sounding)
%%addWetbulb
	%Function to add wetbulb field to a soundings structure. Wetbulb is
	%calculated numerically from temperature, dewpoint, and pressure.
    %
    %General form: [wetSound] = addWetbulb(sounding)
    %
    %Output
    %wetSound: sounding structure with calculated wetbulb temperature
    %errorTracker: array containing the indices of soundings that
    %encountered errors in the wetbulb calculation
    %
    %Input
    %sounding: sounding structure that must already contain dewpoint
    %
    %For IGRA processing: works best if level 3 data has been filtered out.
    %Otherwise, wetbulb field will have a different size then other fields,
    %complicating any further analysis.
    %
    %This function is spectacularly slow thanks to the nested for loops
    %and numerical algebraic evaluation. It's sually best to run on the smallest
    %dataset possible, after all other filtration has been applied.
    %
    %Version date: 9/27/2019
    %Last major revision: 3/18/2018
    %Written by: Daniel Hueholt
    %North Carolina State University
    %Undergraduate Research Assistant at Environment Analytics
    %
    %See also wetbulb
    %

wetSound = sounding;

%Decided not to include a check for dewpoint based on the the dewpt field, in case
%future users/future me writes different processing code and uses a different
%fieldname such as dewpoint or dew.
    
errorTracker = NaN(1,length(sounding)+1); %Initialize error tracking matrix
ec = 1; %Initialize error counter
for soundLoop = length(sounding):-1:1
    disp(soundLoop); %Display current sounding number within the soundings structure to track progress, otherwise all hope will be lost
    %tic
    for levelLoop = length(sounding(soundLoop).temp):-1:1 %Backwards loop saves precious, precious time
        try %Calculation will fail if pressure, dewpoint, or temperature are NaNs
            [wetSound(soundLoop).wetbulb(levelLoop)] = wetbulb(sounding(soundLoop).pressure(levelLoop)./100,sounding(soundLoop).dewpt(levelLoop),sounding(soundLoop).temp(levelLoop)); %Pressure is in Pa in IGRA, but must be in hPa for wetbulb calculation
        catch ME; %#ok
            if ismember(soundLoop,errorTracker) %If an error corresponding to the current index has already been logged
                continue %then don't log it again
            else %If an error corresponding to the current index has not been logged before
                errorTracker(ec) = soundLoop; %Record the index
                ec = ec+1; %Increment the error counter
                continue %move on
            end
        end
    end
    %toc %Fun to display time elapsed to add wetbulb for each sounding
end

errorTracker(isnan(errorTracker)==1) = []; %Retain only entries with errors
errorTracker = sort(errorTracker); %Otherwise indices will be in reverse order thanks to the backwards loop

end