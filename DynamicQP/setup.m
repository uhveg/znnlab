clear;close all;clc;
% Minimize:
f = @(x, t) (sin(t)/4 + 1)*x(1)^2 + (cos(t)/4 + 1)*x(2)^2 ...
            + cos(t)*x(1)*x(2) + sin(3*t)*x(1) + cos(3*t)*x(2);
% Subject to:
c = @(x, t) sin(4*t)*x(1) + cos(4*t)*x(2) - cos(2*t);

% ZNN model parameters
tau = 0.01;gamma = 0.4/tau;h = tau*gamma;

y0 = ones(3, 1);W0 = ones(3); u0 = ones(3, 1);
y1 = ones(3, 1);W1 = ones(3); u1 = ones(3, 1);
y2 = ones(3, 1);

% Run simulation
output1 = sim('EULER_TYPE_ZNNK.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));
output2 = sim('EULER_TYPE_ZNNU.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));
output3 = sim('TAYLOR_TYPE_ZNNK.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));
output4 = sim('TAYLOR_TYPE_ZNNU.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));

outs = {output1, output2, output3, output4};
for o=1:numel(outs)
    output = outs{o};
    figure('OuterPosition',[360,90,1200,900], 'Name', ...
        strcat(output.SimulationMetadata.ModelInfo.ModelName, ': QP'));
    subplot(2,1,1);hold on;grid minor;
    xlabel('tiempo(s)', 'Interpreter', 'latex');
    title('$f(x,t) = ((\sin t) / 4+1) x_1^2(t)+((\cos t) / 4+1) x_2^2(t) +\cos t x_1(t) x_2(t)+\sin 3 t x_1(t)+\cos 3 t x_2(t)$', 'Interpreter', 'latex');
    plot(output.f.Time, output.f.Data);
    axes('position',[.6 .7 .28 .2]);box on;grid minor;hold on;
    % set(gca, 'YScale', 'log');
    set(gca, 'YLimSpec', 'Padded');
    indexOfInterest = (output.f.Time > 5);
    plot(output.f.Time(indexOfInterest), output.f.Data(indexOfInterest));
    subplot(2,1,2);hold on;grid minor;
    xlabel('tiempo(s)', 'Interpreter', 'latex');
    title('$|\sin 4 t x_1(t)+\cos 4 t x_2(t)-\cos 2 t|^2$', 'Interpreter', 'latex');
    plot(output.c.Time, output.c.Data.^2);
    set(gca, 'YLimSpec', 'Padded');
    axes('position',[.6 .21 .28 .2]);box on;grid minor;hold on;
    set(gca, 'YScale', 'log');
    set(gca, 'YLimSpec', 'Padded');
    indexOfInterest = (output.c.Time > 5);
    plot(output.c.Time(indexOfInterest), output.c.Data(indexOfInterest).^2);

    
    figure('OuterPosition',[360,90,1200,900], 'Name', ...
        strcat(output.SimulationMetadata.ModelInfo.ModelName, ': Estados'));
    vartitle = {'$x_1$', '$x_2$', '$\lambda$'};
    for i=1:3
        subplot(3,1,i);hold on; grid minor;
        titleHandle = title(vartitle(i), 'Interpreter', 'latex');
        set(titleHandle, 'Units', 'normalized', 'Position', [0.5, 0.85, 0]);
        plot(output.y.Time, output.y.Data(:,i));
    end
end

figure;hold on;grid minor;
title('$\| W_k\mathbf{y}_k - \mathbf{u}_k \|$', 'Interpreter', 'latex');
ylabel('error');
xlabel('tiempo(s)');
h1=plot(output1.e.Time, vecnorm(output1.e.Data')');
h2=plot(output2.e.Time, vecnorm(output2.e.Data')', '--');
h3=plot(output3.e.Time, vecnorm(output3.e.Data')');
h4=plot(output4.e.Time, vecnorm(output4.e.Data')', '--');
set(gca, 'YScale', 'log');
set(gca, 'YLimSpec', 'Padded');
legend_labels = {'ETDTZNNK', 'ETDTZNNU', 'TTDTZNNK', 'TTDTZNNU'};
hL = legend([h1, h2, h3, h4], legend_labels);